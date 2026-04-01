"""Declarative variant specification for room acoustic treatment.

This module provides dataclasses for defining room treatment variants as
declarative data specs, and an ``apply_variant`` function that applies such
a spec to a copy of a base room.

Usage Example
-------------
Define actions and compose variant specs:

>>> from sapyne.variants import VariantSpec, AddSurface, AddObject, apply_variant
>>>
>>> _v1_actions = [
...     AddSurface("novatop", "NVT005", 11.05,
...                subtract_area_from="Stěny", mode="accumulate"),
...     AddObject("ecophon_objects", "ECO001", 13.6),
... ]
>>>
>>> VARIANT_SPECS = {
...     "v1": VariantSpec("Varianta 1", "Základní opatření", actions=_v1_actions),
...     "v2": VariantSpec("Varianta 2", "Základní + podhled",
...                       actions=_v1_actions + [
...                           AddSurface("rigips", "RIG047", 24.0,
...                                      subtract_area_from="Strop"),
...                       ]),
... }
>>>
>>> rooms = {key: apply_variant(room_base, spec, libraries)
...          for key, spec in VARIANT_SPECS.items()}

Classes
-------
- ``AddSurface``: Action spec for adding a surface to the room.
- ``AddObject``: Action spec for adding an object to the room.
- ``VariantSpec``: Aggregates a list of actions into a named variant.

Functions
---------
- ``apply_variant``: Apply a ``VariantSpec`` to a deep copy of a base room.
"""

import copy
from dataclasses import dataclass, field
from typing import Optional

from pandas import DataFrame


@dataclass
class AddSurface:
    """Declarative spec for adding a surface to a room.

    Parameters
    ----------
    library_key : str
        Key in the ``libraries`` dict passed to :func:`apply_variant`,
        e.g. ``"novatop"`` or ``"rigips"``.
    material_id : str
        ``ID`` column value of the material row in the referenced library.
    area : float
        Surface area [m²].
    renamed_surface : str, optional
        Override the material's display name.
    subtract_area_from : str, optional
        ``SurfaceID`` (or unique ``Name``) of the surface whose effective area
        should be reduced by this surface's area.  Use this for panels that are
        mounted on an existing surface (e.g. wall treatment).
    surface_id : str, optional
        Stable ``SurfaceID`` for this entry.  When omitted the room logic
        reuses an existing entry with the same name or generates a new id.
    replace_surface_id : str, optional
        Explicit ``SurfaceID`` reference used instead of
        ``subtract_area_from`` when you need to address a surface by ID.
    mode : str, optional
        ``"overwrite"`` (default) or ``"accumulate"``.  Use ``"accumulate"``
        when the same material is added in multiple spans on the same host
        surface (multiple panels on one wall).
    comment : str, optional
        Human-readable annotation; not used in calculations.
    """

    library_key: str
    material_id: str
    area: float
    renamed_surface: Optional[str] = None
    subtract_area_from: Optional[str] = None
    surface_id: Optional[str] = None
    replace_surface_id: Optional[str] = None
    mode: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class AddObject:
    """Declarative spec for adding an object to a room.

    Parameters
    ----------
    library_key : str
        Key in the ``libraries`` dict passed to :func:`apply_variant`,
        e.g. ``"ecophon_objects"`` or ``"objects"``.
    material_id : str
        ``ID`` column value of the object row in the referenced library.
    amount : float
        Number of objects or effective absorbing area [m²], depending on
        the library convention.
    renamed : str, optional
        Override the object's display name.
    comment : str, optional
        Human-readable annotation; not used in calculations.
    """

    library_key: str
    material_id: str
    amount: float
    renamed: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class VariantSpec:
    """Named collection of room treatment actions.

    Parameters
    ----------
    name : str
        Short display name for the variant (e.g. ``"Varianta 1"``).
    description : str, optional
        Longer description of the variant's intent.
    actions : list of AddSurface or AddObject
        Ordered list of treatment actions to apply to the base room.
        Actions are applied in the order they are listed.

    Notes
    -----
    To compose variants incrementally, reuse a shared action list and extend
    it with additional steps:

    >>> v1_actions = [AddSurface(...), AddObject(...)]
    >>> v2_actions = v1_actions + [AddSurface(...)]  # variant 2 builds on v1
    """

    name: str
    description: str = ""
    actions: list = field(default_factory=list)


def apply_variant(
    base_room,
    spec: VariantSpec,
    libraries: dict,
) -> object:
    """Apply a :class:`VariantSpec` to a deep copy of *base_room*.

    The base room is never modified.  A fresh deep copy is created for
    each call so variants are independent of each other.

    Parameters
    ----------
    base_room : sapyne.room.Room
        Calibrated base room (bare surfaces, no treatment).  Will be
        deep-copied before actions are applied.
    spec : VariantSpec
        Declarative spec describing the treatment to add.
    libraries : dict of str -> pandas.DataFrame
        Mapping from library key (e.g. ``"novatop"``) to the corresponding
        material DataFrame.  The keys must match the ``library_key``
        attributes used in the spec's actions.

    Returns
    -------
    sapyne.room.Room
        A new room instance with all actions from *spec* applied and
        ``update_absorption()`` already called.

    Raises
    ------
    ValueError
        If a ``library_key`` referenced in an action is absent from
        *libraries*, or if the action itself is malformed (invalid
        ``material_id``, area exceeding host surface, etc.).
    TypeError
        If an action is of an unknown type.
    """
    room_copy = copy.deepcopy(base_room)

    for action in spec.actions:
        if isinstance(action, AddSurface):
            lib = _resolve_library(libraries, action.library_key, action)
            room_copy.add_surface(
                library=lib,
                material_id=action.material_id,
                area=action.area,
                renamed_surface=action.renamed_surface,
                subtract_area_from=action.subtract_area_from,
                surface_id=action.surface_id,
                replace_surface_id=action.replace_surface_id,
                mode=action.mode,
            )
        elif isinstance(action, AddObject):
            lib = _resolve_library(libraries, action.library_key, action)
            room_copy.add_object(
                library=lib,
                material_id=action.material_id,
                amount=action.amount,
                renamed=action.renamed,
            )
        else:
            raise TypeError(
                f"Unknown action type '{type(action).__name__}'. "
                "Expected AddSurface or AddObject."
            )

    room_copy.update_absorption()
    return room_copy


def _resolve_library(libraries: dict, key: str, action) -> DataFrame:
    """Return the library DataFrame for *key*, raising a clear error if absent.

    Parameters
    ----------
    libraries : dict
        Library mapping passed to :func:`apply_variant`.
    key : str
        Key to look up.
    action : AddSurface or AddObject
        Action that triggered the lookup (used in the error message).

    Returns
    -------
    pandas.DataFrame
        The library DataFrame.

    Raises
    ------
    ValueError
        If *key* is not present in *libraries*.
    """
    if key not in libraries:
        available = list(libraries.keys())
        raise ValueError(
            f"Library key '{key}' not found for action {action!r}. "
            f"Available keys: {available}"
        )
    return libraries[key]
