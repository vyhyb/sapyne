"""Calibration of modeled room absorption to measured reverberation time.

This module provides optimization utilities that fit an equivalent absorption
object so model outputs match measured band-wise ``T60`` values.
"""

from .models import t60_csn730525
from .room import BANDS, AREA, Room

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution


def model_calibration(
    room: Room,
    t60_experiment_arr: np.ndarray,
    attenuation_arr: np.ndarray,
):
    """Calibrate a room model against measured ``T60`` values.

    Parameters
    ----------
    room : Room
        Room instance with current surfaces/objects definition.
    t60_experiment_arr : np.ndarray
        Measured reverberation times for bands in ``BANDS``.
    attenuation_arr : np.ndarray
        Air attenuation coefficients for bands in ``BANDS``.

    Returns
    -------
    list
        List of SciPy optimization results, one per frequency band.
    """

    def objective(absorption, t60_experiment, band, surface_sum, attenuation):
        # update absorption
        room.objects.iloc[-1, room.objects.columns.get_loc(band)] = absorption[0]
        room.update_absorption()

        # calculate T60
        t60 = t60_csn730525(
            room.absorption,
            room.volume,
            surface_sum,
            attenuation=attenuation,
            constant=0.164,
        )[band]

        # calculate the objective function
        chi2 = (t60 - t60_experiment) ** 2
        print(chi2)
        return chi2

    object_dict = {
        "ID": "EXP001",
        "Name": "Dopočet pohltivosti dle měření",
        "Amount": 1,
    }
    object_series = pd.Series(object_dict)
    for band in BANDS:
        object_series[band] = 1

    room.objects = pd.concat(
        [room.objects, object_series.to_frame().T], ignore_index=True
    )
    surface_sum = room.surfaces.loc[:, AREA].sum()

    # run the optimization band by band
    result = []
    for i, band in enumerate(BANDS):
        bounds_band = [(1e-6, 100)]  # Set bounds for the current band
        # Run the optimization for the current band
        res = differential_evolution(
            objective,
            bounds_band,
            args=(t60_experiment_arr[i], band, surface_sum, attenuation_arr[i]),
            strategy="best1bin",
            maxiter=100000,
            popsize=1,
            tol=1e-6,
        )
        result.append(res)
    return result
