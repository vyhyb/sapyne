"""Module for importing reverberation data from Dirac and REW.
The module contains classes for importing reverberation data from
Dirac and REW. The data is stored in a pandas DataFrame format.

Classes:
--------
DiracReverberationData
REWReverberationData

Functions:
----------
merge_rew_dfs

Notes
-----
The DiracReverberationData class is used to import reverberation data
from a txt file exported from Dirac, which typically contains more than
one measurement. 

The REWReverberationData class is used to import reverberation data from
a txt file exported from REW. Such measurement is typically a single 
measurement containing various quantities. In order to merge multiple
measurements of one quantity, the merge_rew_dfs function is used.

REW_QUANTITIES is a list of possible quantities that can be merged using
the merge_rew_dfs function.
"""

from typing import List
import pandas as pd
import numpy as np
import re

class DiracReverberationData:
    """Representation of Dirac exported reverberation data.
    
    The object contains the data from the txt file exported from Dirac 
    in a form of a pandas DataFrame.

    Structure:
    ----------
    path : str
        Path to the data file.
    df : pandas.DataFrame
        Reverberation data in a DataFrame format. Columns are the 
        frequency bands and the rows are the individual measurements.
    cols : np.ndarray
        Frequency bands of the data.
    """
    def __init__(self, path):
        """load the data from the given path.

        Parameters
        ----------
        path : str
            Path to the data txt file.
        """
        self.path = path
        self.load_data()

    def load_data(self):
        """Load the data from the file."""
        self.df = pd.read_csv(self.path, sep='\t', decimal=',')
        # drop the first row of the data
        self.df = self.df.drop(0)
        # drop the row having "Number of Measurements" in the first column and the following rows
        row_idx = self.df[self.df.iloc[:,0].str.strip() == "Number of Measurements"].index
        self.df = self.df.iloc[:row_idx[0]-1]
        self.df = self.df.drop(columns=self.df.columns[0])
        self.cols = np.array(self.df.columns).astype(float)

REW_QUANTITIES = [
    "EDT (s)", "T20 (s)", "T30 (s)", "Topt (s)", 
    "ToptStart (dB)", "ToptEnd (dB)", "T60M (s)", "C50 (dB)", "C80 (dB)", 
    "D50 (%)", "TS (s)"
]

class REWReverberationData:
    """Representation of REW reverberation data file.
    """
    def __init__(self, path, bands="octave"):
        """
        Initialize the REWReverberationData by importing the data from 
        the specified text file previously exported from REW.

        Parameters
        ----------
        path : str
            Path to the REW data file.
        bands : str, optional
            Band resolution of the data. Can be either "octave" or "third". Default is "octave".
        """
        self.path = path
        self.bands = bands
        if bands == "octave":
            filt_str = "1/1"
        elif bands == "third":
            filt_str = "1/3"

        pattern = re.compile(filt_str)
        with open(path) as f:
            valid_lines = []
            for lineno, line in enumerate(f):
                matches = pattern.finditer(line)
                for m in matches:
                    # aad the line number to the list if the line starts with a number
                    if line[0].isdigit():
                        valid_lines.append(lineno)

        try:
            assert len(valid_lines) > 0
        except AssertionError:
            raise ValueError("No valid lines found in the file for the specified band resolution. ({})".format(filt_str))

        pattern = re.compile("Format is ")
        with open(path) as f:
            for lineno, line in enumerate(f):
                matches = pattern.finditer(line)
                for m in matches:
                    cols = line.strip("\n")
                    cols = r"'" + cols.replace(", ", r"', '")[len("Format is "):] + r"'"
                    cols = list(eval(cols))
        
        with open(path) as f:
            self.metadata = ''.join([next(f) for _ in range(10)])
        
        for idx, c in enumerate(cols):
            if c == 'r':
                cols[idx] += "_"+cols[idx-1]
        
        self.cols = cols
        
        self.df = pd.read_csv(path, skiprows=valid_lines[0]-1, names=cols, nrows=valid_lines[-1]-valid_lines[0]+1)

def merge_rew_dfs(
        data: List[REWReverberationData],
        quantity: str = "T20 (s)"
    ) -> pd.DataFrame:
    """Merge the REW dataframes for the specified quantity.
    The possible quantities are listed in the REW_QUANTITIES list.

    Parameters
    ----------
    data : List[REWReverberationData]
        List of REWReverberationData objects.
    quantity : str, optional
        Quantity to merge. Default is "T20 (s)".

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with swaped columns and rows. 
        (rows are the measurements, columns are the Frequency bands)
    """
    try:
        assert quantity in REW_QUANTITIES
    except AssertionError:
        raise ValueError("The quantity specified is not valid. ({}), valid quantities are: {}".format(quantity, REW_QUANTITIES))
    data_dict = {}
    for d in data:
        data_dict[d.path] = d.df[quantity]
    df = pd.DataFrame(data_dict)
    df = df.T
    df.columns = d.df["Frequency"]
    return df