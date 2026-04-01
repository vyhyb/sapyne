"""Room object for reverberation time calculations
according to Sabine and similar models.

This module provides a Room object for calculating the reverberation time
according to Sabine and similar models. The Room object can be used to
store data about the room, such as volume, temperature, humidity, pressure,
surfaces, and objects. The Room object can also calculate the absorption
coefficients of the surfaces and objects, and calculate the mean absorption
coefficient for each frequency band.

Classes
-------
- `Room`: Room object for reverberation time calculations.
"""

from pandas import DataFrame
import pandas as pd
from typing import Optional

BANDS = ["125", "250", "500", "1000", "2000", "4000"]
IDENTIFIERS = ["ID", "Name"]
AREA = "Area"
AMOUNT = "Amount"
SURFACE_ID = "SurfaceID"
REPLACES_SURFACE_ID = "ReplacesSurfaceID"
EFFECTIVE_AREA = "EffectiveArea"
SURFACE_MODES = {"overwrite", "accumulate"}


class Room:
    """Room object for reverberation time calculations
    according to Sabine and similar models.
    """

    def __init__(
        self,
        name: str,
        description: str,
        volume: float,
        temperature: float,
        humidity: float,
        pressure: float,
        surfaces: Optional[DataFrame] = None,
        objects: Optional[DataFrame] = None,
        surface_update_mode: str = "overwrite",
    ):
        """Room object for reverberation time calculations
        according to Sabine and similar models.

        Parameters
        ----------
        name : str
            Name of the room
        description : str
            Short description of the room
        volume : float
            Net volume of the room [m^3]
        temperature : float
            Assumed temperature in the room [degC]
        humidity : float
            Assumed relative humidity [%]
        pressure : float
            Assumed atmospheric pressure [kPa]
        surfaces : DataFrame
            pandas.DataFrame containing absorption coefficient data.
            The required columns are:
            - "ID" (material id from the library)
            - "Name" (material name from the library)
            - "Area" (area in the room)
            - 125 ... 4000 (central frequencies of the octave bands
                    typically used in room acoustics)
        objects : DataFrame
            pandas.DataFrame containing absorption data about objects.
            The required columns are:
            The required columns are:
            - "ID" (material id from the library)
            - "Name" (material name from the library)
            - "Amount" (amount in the room)
            - 125 ... 4000 (absorption coefficient for the octave bands
                    typically used in room acoustics)

        """
        self.name = name
        self.description = description
        self.volume = volume
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        if surface_update_mode not in SURFACE_MODES:
            raise ValueError(f"surface_update_mode must be one of {SURFACE_MODES}")
        self.surface_update_mode = surface_update_mode
        self.surfaces = self._normalize_surfaces(surfaces)
        self.objects = self._normalize_objects(objects)
        self.absorption = None
        self.resolved_surfaces = None

    @staticmethod
    def _required_surface_columns() -> list:
        return IDENTIFIERS + [AREA] + BANDS

    @staticmethod
    def _required_object_columns() -> list:
        return IDENTIFIERS + [AMOUNT] + BANDS

    def _normalize_surfaces(self, surfaces: Optional[DataFrame]) -> DataFrame:
        columns = self._required_surface_columns() + [SURFACE_ID, REPLACES_SURFACE_ID]
        if surfaces is None:
            return DataFrame(columns=columns)

        normalized = surfaces.copy()
        missing = [
            col
            for col in self._required_surface_columns()
            if col not in normalized.columns
        ]
        if missing:
            raise ValueError(f"Missing required surface columns: {missing}")

        if SURFACE_ID not in normalized.columns:
            normalized.loc[:, SURFACE_ID] = pd.NA
        if REPLACES_SURFACE_ID not in normalized.columns:
            normalized.loc[:, REPLACES_SURFACE_ID] = pd.NA

        normalized = self._assign_missing_surface_ids(normalized)
        normalized.loc[:, AREA] = pd.to_numeric(normalized.loc[:, AREA], errors="raise")
        return normalized

    def _normalize_objects(self, objects: Optional[DataFrame]) -> DataFrame:
        columns = self._required_object_columns()
        if objects is None:
            return DataFrame(columns=columns)

        normalized = objects.copy()
        missing = [col for col in columns if col not in normalized.columns]
        if missing:
            raise ValueError(f"Missing required object columns: {missing}")

        normalized.loc[:, AMOUNT] = pd.to_numeric(
            normalized.loc[:, AMOUNT], errors="raise"
        )
        return normalized

    def _make_unique_surface_id(self, requested_id: str, used_ids: set) -> str:
        base_id = str(requested_id).strip() if requested_id is not None else ""
        if base_id == "":
            base_id = "surface"

        candidate = base_id
        suffix = 2
        while candidate in used_ids:
            candidate = f"{base_id}_{suffix}"
            suffix += 1
        return candidate

    def _assign_missing_surface_ids(self, surfaces: DataFrame) -> DataFrame:
        normalized = surfaces.copy()
        used_ids = set()

        for index, row in normalized.iterrows():
            current_id = row.get(SURFACE_ID, pd.NA)
            if pd.isna(current_id) or str(current_id).strip() == "":
                requested = row.get("Name", "surface")
            else:
                requested = str(current_id)

            unique_id = self._make_unique_surface_id(requested, used_ids)
            used_ids.add(unique_id)
            normalized.loc[index, SURFACE_ID] = unique_id

        return normalized

    def _resolve_reference_surface_id(self, reference: str, surfaces: DataFrame) -> str:
        by_id = surfaces.loc[surfaces[SURFACE_ID] == reference, SURFACE_ID]
        if len(by_id) == 1:
            return by_id.iloc[0]
        if len(by_id) > 1:
            raise ValueError(
                f"Surface reference '{reference}' is not unique by SurfaceID"
            )

        by_name = surfaces.loc[surfaces["Name"] == reference, SURFACE_ID]
        if len(by_name) == 1:
            return by_name.iloc[0]
        if len(by_name) > 1:
            raise ValueError(
                f"Surface reference '{reference}' is ambiguous by Name. "
                "Use an explicit surface_id."
            )

        raise ValueError(f"Surface reference '{reference}' not found in the room")

    def _compute_resolved_surfaces(
        self, surfaces: Optional[DataFrame] = None, validate: bool = False
    ) -> DataFrame:
        source = self.surfaces if surfaces is None else surfaces
        if source.empty:
            return source.copy()

        resolved = source.copy()
        resolved.loc[:, AREA] = pd.to_numeric(resolved.loc[:, AREA], errors="raise")

        covered_area = (
            resolved.loc[resolved[REPLACES_SURFACE_ID].notna()]
            .groupby(REPLACES_SURFACE_ID, as_index=True)[AREA]
            .sum()
        )

        resolved.loc[:, "_covered_area"] = (
            resolved[SURFACE_ID].map(covered_area).fillna(0.0)
        )
        resolved.loc[:, EFFECTIVE_AREA] = resolved[AREA] - resolved["_covered_area"]

        if validate:
            invalid = resolved.loc[
                resolved[EFFECTIVE_AREA] < -1e-9, [SURFACE_ID, "Name", EFFECTIVE_AREA]
            ]
            if not invalid.empty:
                problem_ids = ", ".join(invalid[SURFACE_ID].astype(str).tolist())
                raise ValueError(
                    "Replacement areas exceed available area for: " f"{problem_ids}."
                )

        resolved.loc[resolved[EFFECTIVE_AREA] < 0, EFFECTIVE_AREA] = 0.0
        return resolved.drop(columns=["_covered_area"])

    def resolve_surfaces(self) -> DataFrame:
        resolved = self._compute_resolved_surfaces(validate=True)
        result = resolved.copy()
        if not result.empty:
            result.loc[:, AREA] = result.loc[:, EFFECTIVE_AREA]
            result = result.drop(columns=[EFFECTIVE_AREA])
        self.resolved_surfaces = result
        return result

    def resolve_objects(self) -> DataFrame:
        return self.objects.copy()

    def add_surface(
        self,
        library: DataFrame,
        material_id: str,
        area: float,
        subtract_area_from=None,
        renamed_surface=None,
        surface_id: Optional[str] = None,
        replace_surface_id: Optional[str] = None,
        mode: Optional[str] = None,
    ):
        """Add a surface to the room.

        Parameters
        ----------
        library : DataFrame
            pandas.DataFrame containing absorption coefficient data.
            The required columns are:
            - "ID" (material id from the library)
            - "Name" (material name from the library)
            - 125 ... 4000 (central frequencies of the octave bands
                    typically used in room acoustics)
        material_id : str
            ID of the material in the library
        area : float
            Area of the surface [m^2]
        subtract_area_from : str
            SurfaceID (or unique Name for backward compatibility)
            of the surface to subtract area from.
            This is useful for windows and doors, where the area
            is subtracted from the wall area.
        surface_id : str
            Stable SurfaceID for this entry. If omitted, an existing
            unique Name is reused, otherwise a new SurfaceID is generated.
        replace_surface_id : str
            Preferred explicit SurfaceID reference of the replaced surface.
        mode : str
            "overwrite" or "accumulate" behavior when this surface already exists.
        """
        if replace_surface_id is not None and subtract_area_from is not None:
            raise ValueError(
                "Use either replace_surface_id or subtract_area_from, not both"
            )

        active_mode = self.surface_update_mode if mode is None else mode
        if active_mode not in SURFACE_MODES:
            raise ValueError(f"mode must be one of {SURFACE_MODES}")

        material = library.loc[library["ID"] == material_id].copy()
        if material.empty:
            raise ValueError("Material ID not found in the library")
        material = material.iloc[[0]].copy()

        if renamed_surface is not None:
            material.loc[:, "Name"] = renamed_surface

        requested_target = (
            replace_surface_id if replace_surface_id is not None else subtract_area_from
        )
        prospective = self.surfaces.copy()
        target_surface_id = None
        if requested_target is not None:
            target_surface_id = self._resolve_reference_surface_id(
                requested_target, prospective
            )

        new_name = material.loc[:, "Name"].iloc[0]
        if surface_id is None:
            same_name = prospective.loc[prospective["Name"] == new_name, SURFACE_ID]
            if len(same_name) > 1:
                raise ValueError(
                    f"Multiple surfaces share Name '{new_name}'. Provide explicit surface_id."
                )
            if len(same_name) == 1:
                resolved_surface_id = same_name.iloc[0]
            else:
                used_ids = set(prospective[SURFACE_ID].dropna().astype(str).tolist())
                resolved_surface_id = self._make_unique_surface_id(new_name, used_ids)
        else:
            resolved_surface_id = str(surface_id)

        if target_surface_id is not None and target_surface_id == resolved_surface_id:
            raise ValueError("A surface cannot replace itself")

        target_row = prospective.loc[prospective[SURFACE_ID] == resolved_surface_id]
        new_area = float(area)
        if len(target_row) > 1:
            raise ValueError(
                f"SurfaceID '{resolved_surface_id}' is duplicated in room surfaces"
            )

        if len(target_row) == 1:
            idx = target_row.index[0]
            updated_area = (
                new_area
                if active_mode == "overwrite"
                else float(prospective.loc[idx, AREA]) + new_area
            )
            replaced_surface_value = (
                target_surface_id
                if requested_target is not None
                else prospective.loc[idx, REPLACES_SURFACE_ID]
            )
            prospective.loc[idx, IDENTIFIERS] = material.loc[
                material.index[0], IDENTIFIERS
            ].values
            prospective.loc[idx, BANDS] = material.loc[material.index[0], BANDS].values
            prospective.loc[idx, AREA] = updated_area
            prospective.loc[idx, REPLACES_SURFACE_ID] = replaced_surface_value
        else:
            new_row = material.iloc[0].to_dict()
            new_row[AREA] = new_area
            new_row[SURFACE_ID] = resolved_surface_id
            new_row[REPLACES_SURFACE_ID] = target_surface_id
            prospective = pd.concat(
                [prospective, pd.DataFrame([new_row])], ignore_index=True
            )

        self._compute_resolved_surfaces(prospective, validate=True)
        self.surfaces = prospective.reset_index(drop=True)

    def add_object(
        self, library: DataFrame, material_id: str, amount: float, renamed: str = None
    ):
        """Add an object to the room.

        Parameters
        ----------
        library : DataFrame
            pandas.DataFrame containing absorption coefficient data.
            The required columns are:
            - "ID" (material id from the library)
            - "Name" (material name from the library)
            - 125 ... 4000 (central frequencies of the octave bands
                    typically used in room acoustics)
        material_id : str
            ID of the material in the library
        amount : float
            Amount of the object in the room [m^2]
        """
        material = library.loc[library["ID"] == material_id].copy()
        if material.empty:
            raise ValueError("Material ID not found in the library")
        material = material.iloc[[0]].copy()

        material.loc[:, "Amount"] = amount

        if renamed is not None:
            material.loc[:, "Name"] = renamed

        # check if the material is already in the objects
        if material.loc[:, "Name"].values[0] in self.objects["Name"].values:
            # if it is, overwrite the area
            self.objects.loc[
                self.objects["Name"] == material.loc[:, "Name"].values[0], "Amount"
            ] = amount
        else:
            self.objects = pd.concat([self.objects, material], ignore_index=True)

    def update_absorption(self):
        # does a complete recalculation. TODO think of a more efficient way.
        resolved_surfaces = self.resolve_surfaces()
        absorption_surfaces = resolved_surfaces[IDENTIFIERS].copy()
        absorption_objects = self.objects[IDENTIFIERS].copy()
        # print(self.surfaces.loc[:, BANDS])
        # print(self.surfaces.loc[:, AREA])
        # print(self.surfaces.loc[:, BANDS].mul(self.surfaces.loc[:, AREA], axis=0))
        absorption_surfaces.loc[:, BANDS] = resolved_surfaces.loc[:, BANDS].mul(
            resolved_surfaces.loc[:, AREA], axis=0
        )
        absorption_objects.loc[:, BANDS] = self.objects.loc[:, BANDS].mul(
            self.objects.loc[:, AMOUNT], axis=0
        )

        self.absorption = pd.concat(
            [absorption_surfaces, absorption_objects], axis=0, ignore_index=True
        )
        return self.absorption
