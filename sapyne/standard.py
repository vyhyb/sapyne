""" This module contains the optimum T60 values given by different standards, 
This module contains the optimum T60 values given by different standards, 
mainly the ČSN 73 0527. It defines various room types and their corresponding 
T60 limits, frequency bands, and optimal T60 dependencies based on room volume.

Constants:
    FREQUENCIES (list): Standard frequency bands.
    FREQUENCIES_EXTENDED (list): Extended frequency bands.
    T60_LIMITS (dict): Dictionary containing T60 limits for different room types.
    T_OPT_DEPENDENCY (dict): Dictionary containing lambda functions to calculate 
                             optimal T60 based on room volume.
    VOLUME_LIMITS (dict): Dictionary containing volume limits for different room types.

Classes:
    RoomType: Dataclass representing a room type with attributes for name, 
              T60 limits, frequencies, optimal T60 dependency, and volume limits.

Variables:
    ROOM_TYPES (dict): Dictionary containing instances of RoomType for various 
                       room types defined by the ČSN 73 0527.
"""

from dataclasses import dataclass
import numpy as np


FREQUENCIES = [125, 250, 500, 1000, 2000, 4000]
FREQUENCIES_EXTENDED = [63, 125, 250, 500, 1000, 2000, 4000, 8000]

T60_LIMITS = {
    "A.2": (
        [1.45, 1.2, 1.2, 1.2, 1.2, 1.2],
        [1, 0.8, 0.8, 0.8, 0.8, 0.65]
    ),
    "A.3": (
        [1.45, 1.2, 1.2, 1.2, 1.2, 1.2],
        [0.8, 0.8, 0.8, 0.8, 0.8, 0.65]
    ),
    "A.4": (
        [1.2, 1.2, 1.2, 1.2, 1.2, 1.2],
        [0.65, 0.8, 0.8, 0.8, 0.8, 0.65]
    ),
    "A.5": (
        [1.55, 1.3, 1.3, 1.3, 1.3, 1.3],
        [0.7, 0.7, 0.7, 0.7, 0.7, 0.7]
    ),
    "A.7": (
        [1.5, 1.3, 1.1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0.9, 0.8, 0.7, 0.6]
    ),
    "A.8": (
        [1.2, 1.2, 1.2, 1.2, 1.2, 1.2],
        [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]
    )
}

T_OPT_DEPENDENCY = {
    "A1-1": lambda volume: 0.3961 * np.log10(volume) - 0.026,
    "A1-2": lambda volume: 0.3582 * np.log10(volume) - 0.061,
    "A1-3": lambda volume: 0.3424 * np.log10(volume) - 0.185,
    "A1-4": lambda volume: 0.1915 * np.log10(volume) + 0.134,
    "A1-5": lambda volume: (0.3961 * np.log10(volume) + 0.023
                            if volume < 3000 
                            else 1.0366 * np.log10(volume) - 2.204),
    "A6": lambda volume: np.array([
        (volume ** 0.2916) / (10 ** 1.1269),
        (volume ** 0.3441) / (10 ** 1.4034)
    ])
}

VOLUME_LIMITS = {
    "A1-1": (600, 20_000),
    "A1-2": (500, 20_000),
    "A1-3": (100, 6_000),
    "A1-4": (200, 10_000),
    "A1-5": (500, 20_000),
    "A6": (100, 20000)
}

@dataclass
class RoomType:
    """ Dataclass for room types """
    name: str
    limits: tuple
    frequencies: list
    t_opt_dependency: callable
    volume_limits: tuple = None

ROOM_TYPES = {
    "Opera": RoomType(
        "Opera", 
        T60_LIMITS["A.2"], 
        FREQUENCIES, 
        T_OPT_DEPENDENCY["A1-1"],
        VOLUME_LIMITS["A1-1"]
        ),
    "Hudební divadlo": RoomType(
        "Hudební divadlo", 
        T60_LIMITS["A.2"], 
        FREQUENCIES, 
        T_OPT_DEPENDENCY["A1-1"],
        VOLUME_LIMITS["A1-1"]
        ),
    "Zkušebna orchestru": RoomType(
        "Zkušebna orchestru", 
        T60_LIMITS["A.2"], 
        FREQUENCIES, 
        T_OPT_DEPENDENCY["A1-2"],
        VOLUME_LIMITS["A1-2"]
    ),
    "Víceúčelový sál": RoomType(
        "Víceúčelový sál", 
        T60_LIMITS["A.3"], 
        FREQUENCIES, 
        T_OPT_DEPENDENCY["A1-2"],
        VOLUME_LIMITS["A1-2"]
    ),
    "Činoherní divadlo": RoomType(
        "Činoherní divadlo", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-3"],
        VOLUME_LIMITS["A1-3"]
    ),
    "Zkušebna činohry": RoomType(
        "Zkušebna činohry", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-3"],
        VOLUME_LIMITS["A1-3"]
    ),
    "Přednáškový sál": RoomType(
        "Přednáškový sál", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-3"],
        VOLUME_LIMITS["A1-3"]
    ),
    "Kino s jednokanálovým zvukem": RoomType(
        "Kino s jednokanálovým zvukem", 
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-4"],
        VOLUME_LIMITS["A1-4"]
    ),
    "Kino s vícekanálovým zvukem analogovým": RoomType(
        "Kino s vícekanálovým zvukem analogovým", 
        T60_LIMITS["A.7"],
        FREQUENCIES_EXTENDED,
        T_OPT_DEPENDENCY["A6"],
        VOLUME_LIMITS["A6"]
    ),
    "Kino s vícekanálovým zvukem digitálním": RoomType(
        "Kino s vícekanálovým zvukem digitálním", 
        T60_LIMITS["A.7"],
        FREQUENCIES_EXTENDED,
        T_OPT_DEPENDENCY["A6"],
        VOLUME_LIMITS["A6"]
    ),
    "Učebna a posluchárna": RoomType(
        "Učebna a posluchárna", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        lambda volume: 0.7, # volume independent
        (0, 250)
    ),
    "Posluchárna": RoomType(
        "Posluchárna", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-3"],
        (250, 20000)
    ),
    "Jazyková učebna (laboratoř)": RoomType(
        "Jazyková učebna (laboratoř)", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        lambda volume: 0.45, # volume independent
        (130, 180)
    ),
    "Audiovizuální učebna": RoomType(
        "Audiovizuální učebna", 
        T60_LIMITS["A.4"],
        FREQUENCIES,
        lambda volume: 0.6, # volume independent
        (200, 200)
    ),
    "Učebna hudební výchovy": RoomType(
        "Učebna hudební výchovy", 
        T60_LIMITS["A.3"],
        FREQUENCIES,
        lambda volume: 0.9, # volume independent
        (200, 200)
    ),
    "Učebna hudební výchovy při reprodukované hudbě": RoomType(
        "Učebna hudební výchovy při reprodukované hudbě", 
        T60_LIMITS["A.3"],
        FREQUENCIES,
        lambda volume: 0.5, # volume independent
        (200, 200)
    ),
    "Učebna hry na individuální nástroje a sólového zpěvu": RoomType(
        "Učebna hry na individuální nástroje a sólového zpěvu", 
        T60_LIMITS["A.3"],
        FREQUENCIES,
        lambda volume: 0.7, # volume independent
        (80, 120)
    ),
    "Učebna orchestrání hry hudebních škol": RoomType(
        "Učebna orchestrání hry hudebních škol", 
        T60_LIMITS["A.2"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-2"],
        VOLUME_LIMITS["A1-2"]
    ),
    "Tělocvična a plavecká hala všech typů škol": RoomType(
        "Tělocvična a plavecká hala všech typů škol", 
        T60_LIMITS["A.8"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-5"],
        VOLUME_LIMITS["A1-5"]
    ),
    "Tělocvičny": RoomType(
        "Tělocvičny", 
        T60_LIMITS["A.8"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-5"],
        VOLUME_LIMITS["A1-5"]
    ),
    "Sportovní haly": RoomType(
        "Sportovní haly", 
        T60_LIMITS["A.8"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-5"],
        VOLUME_LIMITS["A1-5"]
    ),
    "Plavecké haly": RoomType(
        "Plavecké haly", 
        T60_LIMITS["A.8"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-5"],
        VOLUME_LIMITS["A1-5"]
    ),
    "Nádražní haly": RoomType(
        "Nádražní haly", 
        T60_LIMITS["A.8"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-5"],
        VOLUME_LIMITS["A1-5"]
    ),
    "Letištní haly": RoomType(
        "Letištní haly", 
        T60_LIMITS["A.8"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-5"],
        VOLUME_LIMITS["A1-5"]
    ),
    "Haly a dvořany veřejných budov": RoomType(
        "Haly a dvořany veřejných budov", 
        T60_LIMITS["A.3"],
        FREQUENCIES,
        lambda volume: 1.4, # volume independent
        None
    )
}