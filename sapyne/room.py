from pandas import DataFrame
import pandas as pd

BANDS = ["125", "250", "500", "1000", "2000", "4000"]
IDENTIFIERS = ["ID", "Name"]
AREA = "Area"
AMOUNT = "Amount"

class Room:
    def __init__(
            self, 
            name : str, 
            description : str,
            volume : float,
            temperature : float,
            humidity : float,
            pressure: float,
            surfaces : DataFrame,
            objects : DataFrame):
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
            - "name" (material name from the library)
            - "Area" (area in the room)
            - 125 ... 4000 (central frequencies of the octave bands 
                    typically used in room acoustics)
        objects : DataFrame
            pandas.DataFrame containing absorption data about objects.
            The required columns are:
            The required columns are:
            - "ID" (material id from the library)
            - "name" (material name from the library)
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

    def update_absorption(self):
        # does a complete recalculation. TODO think of a more efficient way.
        absorption_surfaces = self.surfaces[IDENTIFIERS]
        absorption_objects = self.objects[IDENTIFIERS]
        
        absorption_surfaces[BANDS] = self.surfaces[BANDS].mul(self.surfaces[AREA])
        absorption_objects[BANDS] = self.objects[BANDS].mul(self.objects[AMOUNT])
        
        self.absorption = pd.concat([
            absorption_surfaces,
            absorption_objects
        ], axis=0)
        return self.absorption        