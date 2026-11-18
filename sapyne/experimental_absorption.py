"""Experimental absorption coefficient utilities.

This module contains helper functions for converting reverberation-time based
measurements into equivalent absorption area and ISO 354 absorption
coefficients.
"""

from typing import Tuple

import numpy as np


def eq_absorption_area(
    volume: float,
    rt_60: float | np.ndarray,
    attenuation_coef: float | np.ndarray = 0,
    speed_sound: float = 343,
):
    r"""
    Returns the equivalent absorption area based on the given parameters.

    Parameters
    ----------
    volume : float
        Room volume. [m³]
    rt_60 : array-like
        Reverberation time. [s]
    attenuation_coef : array-like, optional
        Sound attenuation coefficient in air. Default is 0. [m⁻¹]
    speed_sound : float, optional
        Speed of sound in air. Default is 343. [m/s]

    Returns
    -------
    float
        Equivalent absorption area. [m²]

    Notes
    -----
    The equivalent absorption area $A$ is calculated using the formula:
    $$
    A = \frac{55.3 \cdot V}{c \cdot RT_{60}} - 4 \cdot m \cdot V
    $$
    where:
    - $V$ is the room volume [m³]
    - $RT_{60}$ is the reverberation time [s]
    - $m$ is the sound attenuation coefficient in air [m⁻¹]
    - $c$ is the speed of sound in air [m/s]
    """
    return 55.3 * volume / speed_sound / rt_60 - 4 * attenuation_coef * volume


def absorption_coeff_ISO_354_mean(
    absorption_sample: np.ndarray,
    absorption_reference: np.ndarray,
    specimen_area: float,
) -> np.ndarray:
    r"""Calculate the absorption coefficient using ISO 354 standard.

    Parameters
    ----------
    absorption_sample : np.ndarray
        Total absorption of the room with the sample placed inside. [m²]
    absorption_reference : np.ndarray
        Total absorption of the empty room. [m²]
    specimen_area : float
        Area of the sample specimen. [m²]

    Returns
    -------
    np.ndarray
        Absorption coefficient calculated using ISO 354 standard. [dimensionless]

    Notes
    -----
    The absorption coefficient $\alpha$ is calculated using the formula:
    $$
    \alpha = \frac{A_s - A_r}{S}
    $$
    where:
    - $A_s$ is the total absorption of the room with the sample placed inside [m²]
    - $A_r$ is the total absorption of the empty room [m²]
    - $S$ is the area of the sample specimen [m²]
    """
    return (absorption_sample - absorption_reference) / specimen_area


def absorption_coeff_ISO_354_std(
    absorption_sample_std: np.ndarray,
    absorption_reference_std: np.ndarray,
    specimen_area: float,
) -> np.ndarray:
    r"""Calculate the absorption coefficient standard deviation using
    error propagation of the total absorption.

    Parameters
    ----------
    absorption_sample_std : np.ndarray
        Standard deviation of the total absorption of the room with the
        sample placed inside. [m²]
    absorption_reference_std : np.ndarray
        Standard deviation of the total absorption of the empty room. [m²]
    specimen_area : float
        Area of the sample specimen. [m²]

    Returns
    -------
    np.ndarray
        Absorption coefficient standard deviation calculated using
        standard error propagation. [dimensionless]

    Notes
    -----
    The standard deviation of the absorption coefficient $\sigma_\alpha$ is calculated using the formula:
    $$
    \sigma_\alpha = \frac{\sqrt{\sigma_{A_s}^2 + \sigma_{A_r}^2}}{S}
    $$
    where:
    - $\sigma_{A_s}$ is the standard deviation of the total absorption of the room with the sample placed inside [m²]
    - $\sigma_{A_r}$ is the standard deviation of the total absorption of the empty room [m²]
    - $S$ is the area of the sample specimen [m²]
    """
    return (
        np.sqrt(absorption_sample_std**2 + absorption_reference_std**2) / specimen_area
    )


def absorption_coeff_ISO_354(
    absorption_sample: np.ndarray,
    absorption_reference: np.ndarray,
    absorption_sample_std: np.ndarray,
    absorption_reference_std: np.ndarray,
    specimen_area: float,
) -> Tuple[np.ndarray]:
    r"""Calculate the absorption coefficient using ISO 354 standard.

    Parameters
    ----------
    absorption_sample : np.ndarray
        Total absorption of the room with the sample placed inside. [m²]
    absorption_reference : np.ndarray
        Total absorption of the empty room. [m²]
    absorption_sample_std : np.ndarray
        Standard deviation of the total absorption of the room with the sample placed inside. [m²]
    absorption_reference_std : np.ndarray
        Standard deviation of the total absorption of the empty room. [m²]
    specimen_area : float
        Area of the sample specimen. [m²]

    Returns
    -------
    absorption_coeff : np.ndarray
        Absorption coefficient calculated using ISO 354 standard. [dimensionless]
    absorption_coeff_std : np.ndarray
        Absorption coefficient standard deviation calculated using ISO 354 standard. [dimensionless]

    Notes
    -----
    The absorption coefficient $\alpha$ and its standard deviation $\sigma_\alpha$ are calculated using the formulas:
    $$
    \alpha = \frac{A_s - A_r}{S}
    $$
    $$
    \sigma_\alpha = \frac{\sqrt{\sigma_{A_s}^2 + \sigma_{A_r}^2}}{S}
    $$
    where:
    - $A_s$ is the total absorption of the room with the sample placed inside [m²]
    - $A_r$ is the total absorption of the empty room [m²]
    - $\sigma_{A_s}$ is the standard deviation of the total absorption of the room with the sample placed inside [m²]
    - $\sigma_{A_r}$ is the standard deviation of the total absorption of the empty room [m²]
    - $S$ is the area of the sample specimen [m²]
    """
    absorption_coeff = absorption_coeff_ISO_354_mean(
        absorption_sample, absorption_reference, specimen_area
    )
    absorption_coeff_std = absorption_coeff_ISO_354_std(
        absorption_sample_std, absorption_reference_std, specimen_area
    )
    return absorption_coeff, absorption_coeff_std



def speed_of_sound(temperature: float, reference_temperature = 273.15) -> float:
    r"""Calculate the speed of sound in air based on ISO 9613-1:1993.

    Parameters
    ----------
    temperature : float
        Air temperature at the time of measurement. [degC]
    reference_temperature : float, optional
        Reference temperature (0 °C). Default is 273.15.

    Returns
    -------
    float
        Speed of sound in air. [m/s]

    Notes
    -----
    The speed of sound $c$ is calculated using the formula:
    $$
    c = 343.2 \cdot \sqrt{\frac{T + T_0}{T_0 + 20}}
    $$
    where:
    - $T$ is the temperature [°C]
    - $H$ is the relative humidity [%]
    - $P$ is the atmospheric pressure [kPa]
    - $T_0$ is the reference temperature [K]
    """
    return 343.2 * ((temperature + reference_temperature) / (reference_temperature + 20)) ** 0.5