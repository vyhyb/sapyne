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
    "A.4": ( # for both music and speech
        [1.45, 1.2, 1.2, 1.2, 1.2, 1.2],
        [0.8, 0.8, 0.8, 0.8, 0.8, 0.65]
    ),
    "A.5": ( # for speech
        [1.2, 1.2, 1.2, 1.2, 1.2, 1.2],
        [0.65, 0.8, 0.8, 0.8, 0.8, 0.65]
    ),
    "A.6": ( # for music
        [1.45, 1.2, 1.2, 1.2, 1.2, 1.2],
        [1, 0.8, 0.8, 0.8, 0.8, 0.65]
    ),
    "A.7": ( # limited bandwidth
        [np.nan, 1.2, 1.2, 1.2, 1.2, np.nan],
        [np.nan, 0.8, 0.8, 0.8, 0.8, np.nan]
    )
}

T_OPT_DEPENDENCY = {
    "A1-A": lambda volume: 0.731 * np.log10(volume) - 0.371,
    "A1-B": lambda volume: 0.523 * np.log10(volume) - 0.100,
    "A1-C": lambda volume: 0.430 * np.log10(volume),
    "A1-D": lambda volume: 0.396 * np.log10(volume) - 0.026,
    "A1-E": lambda volume: 0.310 * np.log10(volume) - 0.030,
    "A1-F": lambda volume: 0.250 * np.log10(volume) - 0.030,
    "A1-G": lambda volume: 0.310 * np.log10(volume) - 0.450,
    "A2-A": lambda volume: 0.342 * np.log10(volume) - 0.185,
    "A2-B": lambda volume: 0.300 * np.log10(volume) - 0.200,
    "A2-C1":lambda volume: 0.300 * np.log10(volume) + 0.150,
    "A2-C2":lambda volume: 0.300 * np.log10(volume),
    "A2-D": lambda volume: 0.150 * np.log10(volume),
    "A2-E": lambda volume: np.where(volume < 3000, 
                           0.396 * np.log10(volume) + 0.023,
                           1.036 * np.log10(volume) - 2.204),
    "A3-A": lambda volume: 0.342 * np.log10(volume) - 0.185,
    "A3-B": lambda volume: 0.342 * np.log10(volume) - 0.300,
    "A3-C": lambda volume: 0.650 * np.log10(volume) - 0.800,
}

T_OPT_DEPENDENCY_LATEX = {
    "A1-A": r"$T_{0} = 0.731 \cdot \log_{10}(V) - 0.371$",
    "A1-B": r"$T_{0} = 0.523 \cdot \log_{10}(V) - 0.100$",
    "A1-C": r"$T_{0} = 0.430 \cdot \log_{10}(V)$",
    "A1-D": r"$T_{0} = 0.396 \cdot \log_{10}(V) - 0.026$",
    "A1-E": r"$T_{0} = 0.310 \cdot \log_{10}(V) - 0.030$",
    "A1-F": r"$T_{0} = 0.250 \cdot \log_{10}(V) - 0.030$",
    "A1-G": r"$T_{0} = 0.310 \cdot \log_{10}(V) - 0.450$",
    "A2-A": r"$T_{0} = 0.342 \cdot \log_{10}(V) - 0.185$",
    "A2-B": r"$T_{0} = 0.300 \cdot \log_{10}(V) - 0.200$",
    "A2-C1": r"$T_{0} = 0.300 \cdot \log_{10}(V) + 0.150$",
    "A2-C2": r"$T_{0} = 0.300 \cdot \log_{10}(V)$",
    "A2-D": r"$T_{0} = 0.150 \cdot \log_{10}(V)$",
    "A2-E": r"$T_{0} = \begin{cases} 0.396 \cdot \log_{10}(V) + 0.023, & \text{if } V < 3000 \\ 1.036 \cdot \log_{10}(V) - 2.204, & \text{if } V \geq 3000 \end{cases}$",
    "A3-A": r"$T_{0} = 0.342 \cdot \log_{10}(V) - 0.185$",
    "A3-B": r"$T_{0} = 0.342 \cdot \log_{10}(V) - 0.300$",
    "A3-C": r"$T_{0} = 0.650 \cdot \log_{10}(V) - 0.800$"
}

VOLUME_LIMITS = {
    "A1-A": (800, 30_000),
    "A1-B": (800, 20_000),
    "A1-C": (200, 20_000),
    "A1-D": (300,  3_000),
    "A1-E": (300, 10_000),
    "A1-F": (100, 20_000),
    "A1-G": (100,  4_000),
    "A2-A":  (80,  8_000),
    "A2-B":  (30,    400),
    "A2-C1": (30,    300),
    "A2-C2": (30,    300),
    "A2-D":  (30,    250),
    "A2-E": (200, 50_000),            
    "A3-A":  (50,    500),
    "A3-B":  (50,    300),
    "A3-C": (300, 20_000)
}

@dataclass
class RoomType:
    """ Dataclass for room types """
    name: str
    limits_str: str
    t_opt_dependency_str: str
    limits: tuple
    frequencies: list
    t_opt_dependency: callable
    volume_limits: tuple = None


## A1
# 1. A1-A - Sály s převažující varhanní hudbou  
# 2. A1-B - Sály s převažující orchestrální hudbou  
# 3. A1-C - Sály s převažující komorní hudbou  
# 4. A1-C - Operní sály  
# 5. A1-D - Hudební zkušebny pro akustickou produkci (orchestr, sbor)  
# 6. A1-E - Činoherní divadla  
# 7. A1-E - Víceúčelové sály s převažujícím mluveným slovem bez ozvučení  
# 8. A1-E - Činoherní zkušebny  
# 9. A1-F - Hudební zkušebny pro ozvučenou produkci  
# 10. A1-F - Víceúčelové sály s převažující ozvučenou produkcí  
# 11. A1-F - Elektroakusticky ozvučené prostory  
# 12. A1-G - Kina a další prostory s vícekanálovým zvukovým systémem
## A2
# 1. A2-A - Kmenové učebny, odborné učebny, učebny pracovní výuky, seminární místnosti, posluchárny, denní místnosti mateřských škol  
# 2. A2-A - Hudební učebny  
# 3. A2-B - Jazykové učebny  
# 4. A2-B - Speciální učebny se zvýšeným nárokem na srozumitelnost  
# 5. A2-B - Multimediální učebny  
# 6. A2-B - Hudební učebny s reprodukovanou hudbou  
# 7. A2-B - Učebny pro elektronické a elektrofonické hudební nástroje  
# 8. A2-C1 - Učebny hry na individuální akustické nástroje a učebny zpěvu – horní mez  
# 9. A2-C2 - Učebny hry na individuální akustické nástroje a učebny zpěvu – dolní mez  
# 10. A2-D - Učebny hry na bicí nástroje  
# 11. A2-E - Tělocvičny a sportovní haly, plavecké haly  
# 12. A2-E - Učebny gymnastiky a tance, posilovny, prostory pro fitness
## A3
# 1. A3-A - Zasedací místnosti, jednací místnosti, školicí místnosti  
# 2. A3-B - Videokonferenční místnosti  
# 3. A3-B - Jednací místnosti se zvýšeným nárokem na srozumitelnost (např. cizojazyčná jednání)  
# 4. A3-C - Haly a dvorany veřejných budov (např. nádražní a letištní haly)
ROOM_TYPES = {
    "Sály s převažující varhanní hudbou": RoomType(
        "Sály s převažující varhanní hudbou", 
        "A.6",
        "A1-A",
        T60_LIMITS["A.6"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-A"],
        VOLUME_LIMITS["A1-A"]
    ),
    "Sály s převažující orchestrální hudbou": RoomType(
        "Sály s převažující orchestrální hudbou", 
        "A.6",
        "A1-B",
        T60_LIMITS["A.6"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-B"],
        VOLUME_LIMITS["A1-B"]
    ),
    "Sály s převažující komorní hudbou": RoomType(
        "Sály s převažující komorní hudbou", 
        "A.6",
        "A1-C",
        T60_LIMITS["A.6"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-C"],
        VOLUME_LIMITS["A1-C"]
    ),
    "Operní sály": RoomType(
        "Operní sály", 
        "A.6",
        "A1-C",
        T60_LIMITS["A.6"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-C"],
        VOLUME_LIMITS["A1-C"]
    ),
    "Hudební zkušebny pro akustickou produkci (orchestr, sbor)": RoomType(
        "Hudební zkušebny pro akustickou produkci (orchestr, sbor)", 
        "A.4",
        "A1-D",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-D"],
        VOLUME_LIMITS["A1-D"]
    ),
    "Činoherní divadla": RoomType(
        "Činoherní divadla", 
        "A.5",
        "A1-E",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-E"],
        VOLUME_LIMITS["A1-E"]
    ),
    "Víceúčelové sály s převažujícím mluveným slovem bez ozvučení": RoomType(
        "Víceúčelové sály s převažujícím mluveným slovem bez ozvučení", 
        "A.5",
        "A1-E",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-E"],
        VOLUME_LIMITS["A1-E"]
    ),
    "Činoherní zkušebny": RoomType(
        "Činoherní zkušebny", 
        "A.5",
        "A1-E",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-E"],
        VOLUME_LIMITS["A1-E"]
    ),
    "Hudební zkušebny pro ozvučenou produkci": RoomType(
        "Hudební zkušebny pro ozvučenou produkci", 
        "A.4",
        "A1-F",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-F"],
        VOLUME_LIMITS["A1-F"]
    ),
    "Víceúčelové sály s převažující ozvučenou produkcí": RoomType(
        "Víceúčelové sály s převažující ozvučenou produkcí", 
        "A.4",
        "A1-F",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-F"],
        VOLUME_LIMITS["A1-F"]
    ),
    "Elektroakusticky ozvučené prostory": RoomType(
        "Elektroakusticky ozvučené prostory", 
        "A.4",
        "A1-F",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-F"],
        VOLUME_LIMITS["A1-F"]
    ),
    "Kina a další prostory s vícekanálovým zvukovým systémem": RoomType(
        "Kina a další prostory s vícekanálovým zvukovým systémem", 
        "A.4",
        "A1-G",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A1-G"],
        VOLUME_LIMITS["A1-G"]
    ),
    "Kmenové učebny": RoomType(
        "Kmenové učebny", 
        "A.5",
        "A2-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Odborné učebny": RoomType(
        "Odborné učebny", 
        "A.5",
        "A2-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Učebny pracovní výuky": RoomType(
        "Učebny pracovní výuky", 
        "A.5",
        "A2-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Seminární místnosti": RoomType(
        "Seminární místnosti", 
        "A.5",
        "A2-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Posluchárny": RoomType(
        "Posluchárny", 
        "A.5",
        "A2-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Denní místnosti mateřských škol": RoomType(
        "Denní místnosti mateřských škol", 
        "A.5",
        "A2-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Hudební učebny": RoomType(
        "Hudební učebny", 
        "A.4",
        "A2-A",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-A"],
        VOLUME_LIMITS["A2-A"]
    ),
    "Jazykové učebny": RoomType(
        "Jazykové učebny", 
        "A.5",
        "A2-B",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-B"],
        VOLUME_LIMITS["A2-B"]
    ),
    "Speciální učebny se zvýšeným nárokem na srozumitelnost": RoomType(
        "Speciální učebny se zvýšeným nárokem na srozumitelnost", 
        "A.5",
        "A2-B",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-B"],
        VOLUME_LIMITS["A2-B"]
    ),
    "Multimediální učebny": RoomType(
        "Multimediální učebny", 
        "A.5",
        "A2-B",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-B"],
        VOLUME_LIMITS["A2-B"]
    ),
    "Hudební učebny s reprodukovanou hudbou": RoomType(
        "Hudební učebny s reprodukovanou hudbou", 
        "A.5",
        "A2-B",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-B"],
        VOLUME_LIMITS["A2-B"]
    ),
    "Učebny pro elektronické a elektrofonické hudební nástroje": RoomType(
        "Učebny pro elektronické a elektrofonické hudební nástroje", 
        "A.4",
        "A2-B",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-B"],
        VOLUME_LIMITS["A2-B"]
    ),
    "Učebny hry na individuální akustické nástroje a učebny zpěvu – horní mez": RoomType(
        "Učebny hry na individuální akustické nástroje a učebny zpěvu – horní mez", 
        "A.4",
        "A2-C1",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-C1"],
        VOLUME_LIMITS["A2-C1"]
    ),
    "Učebny hry na individuální akustické nástroje a učebny zpěvu – dolní mez": RoomType(
        "Učebny hry na individuální akustické nástroje a učebny zpěvu – dolní mez", 
        "A.4",
        "A2-C2",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-C2"],
        VOLUME_LIMITS["A2-C2"]
    ),
    "Učebny hry na bicí nástroje": RoomType(
        "Učebny hry na bicí nástroje", 
        "A.4",
        "A2-D",
        T60_LIMITS["A.4"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-D"],
        VOLUME_LIMITS["A2-D"]
    ),
    "Tělocvičny a sportovní haly": RoomType(
        "Tělocvičny a sportovní haly", 
        "A.7",
        "A2-E",
        T60_LIMITS["A.7"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-E"],
        VOLUME_LIMITS["A2-E"]
    ),
    "Plavecké haly": RoomType(
        "Plavecké haly", 
        "A.7",
        "A2-E",
        T60_LIMITS["A.7"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-E"],
        VOLUME_LIMITS["A2-E"]
    ),
    "Učebny gymnastiky a tance": RoomType(
        "Učebny gymnastiky a tance", 
        "A.7",
        "A2-E",
        T60_LIMITS["A.7"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-E"],
        VOLUME_LIMITS["A2-E"]
    ),
    "Posilovny": RoomType(
        "Posilovny", 
        "A.7",
        "A2-E",
        T60_LIMITS["A.7"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-E"],
        VOLUME_LIMITS["A2-E"]
    ),
    "Prostory pro fitness": RoomType(
        "Prostory pro fitness", 
        "A.7",
        "A2-E",
        T60_LIMITS["A.7"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A2-E"],
        VOLUME_LIMITS["A2-E"]
    ),
    "Zasedací místnosti": RoomType(
        "Zasedací místnosti",
        "A.5",
        "A3-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A3-A"],
        VOLUME_LIMITS["A3-A"]
    ),
    "Jednací místnosti": RoomType(
        "Jednací místnosti",
        "A.5",
        "A3-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A3-A"],
        VOLUME_LIMITS["A3-A"]
    ),
    "Školicí místnosti": RoomType(
        "Školicí místnosti",
        "A.5",
        "A3-A",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A3-A"],
        VOLUME_LIMITS["A3-A"]
    ),
    "Videokonferenční místnosti": RoomType(
        "Videokonferenční místnosti",
        "A.5",
        "A3-B",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A3-B"],
        VOLUME_LIMITS["A3-B"]
    ),
    "Jednací místnosti se zvýšeným nárokem na srozumitelnost (např. cizojazyčná jednání)": RoomType(
        "Jednací místnosti se zvýšeným nárokem na srozumitelnost (např. cizojazyčná jednání)",
        "A.5",
        "A3-B",
        T60_LIMITS["A.5"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A3-B"],
        VOLUME_LIMITS["A3-B"]
    ),
    "Haly a dvorany veřejných budov (např. nádražní a letištní haly)": RoomType(
        "Haly a dvorany veřejných budov (např. nádražní a letištní haly)",
        "A.7",
        "A3-C",
        T60_LIMITS["A.7"],
        FREQUENCIES,
        T_OPT_DEPENDENCY["A3-C"],
        VOLUME_LIMITS["A3-C"]
    )
}