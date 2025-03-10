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

BANDS = ["125", "250", "500", "1000", "2000", "4000"]
IDENTIFIERS = ["ID", "Name"]
AREA = "Area"
AMOUNT = "Amount"

class Room:
    """Room object for reverberation time calculations
    according to Sabine and similar models.
    """
    def __init__(
            self, 
            name : str, 
            description : str,
            volume : float,
            temperature : float,
            humidity : float,
            pressure: float,
            surfaces : DataFrame = DataFrame(columns=["ID", "Name", "Area"] + BANDS),
            objects : DataFrame = DataFrame(columns=["ID", "Name", "Amount"] + BANDS)
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
        self.surfaces = surfaces
        self.objects = objects
        self.absorption = None

        # write checks for the required columns in surfaces and objects
        # raise an error if not fulfilled
    def add_surface(
            self, 
            library: DataFrame, 
            material_id: str, 
            area: float, 
            subtract_area_from=None
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
            ID of the surface to subtract the area from. 
            This is useful for windows and doors, where the area 
            is subtracted from the wall area.
        """
        material = library.loc[library["ID"] == material_id].copy()
        if material.empty:
            raise ValueError("Material ID not found in the library")
        
        material.loc[:, "Area"] = area
        if subtract_area_from is not None:
            subtracted_surface = self.surfaces[self.surfaces["ID"] == subtract_area_from]
            if subtracted_surface.empty:
                raise ValueError("Subtracted surface ID not found in the room")
            subtracted_surface.loc[:, "Area"] = subtracted_surface.loc[:, "Area"] - area
            self.surfaces.loc[:, self.surfaces["ID"] == subtract_area_from] = subtracted_surface

        self.surfaces = pd.concat([self.surfaces, material])

    def add_object(
            self, 
            library: DataFrame, 
            material_id: str, 
            amount: float
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
        
        material.loc[:, "Amount"] = amount
        self.objects = pd.concat([self.objects, material])

    def update_absorption(self):
        # does a complete recalculation. TODO think of a more efficient way.
        absorption_surfaces = self.surfaces[IDENTIFIERS]
        absorption_objects = self.objects[IDENTIFIERS]
        print(self.surfaces.loc[:, BANDS])
        print(self.surfaces.loc[:, AREA])
        print(self.surfaces.loc[:, BANDS].mul(self.surfaces.loc[:, AREA], axis=0))
        absorption_surfaces.loc[:, BANDS] = self.surfaces.loc[:, BANDS].mul(self.surfaces.loc[:, AREA], axis=0)
        absorption_objects.loc[:, BANDS] = self.objects.loc[:, BANDS].mul(self.objects.loc[:, AMOUNT], axis=0)
        
        self.absorption = pd.concat([
            absorption_surfaces,
            absorption_objects
        ], axis=0)
        return self.absorption        