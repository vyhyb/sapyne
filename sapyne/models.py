"""
This module provides functions to calculate reverberation time (T60) using different methods:
Sabine, Eyring, Mellington, and CSN 730525. The calculations are based on absorption data,
volume, surface area, and attenuation.

Functions:
    - calc_alpha_mean: Calculate the mean absorption coefficient.
    - t60_sabine: Calculate T60 using the Sabine formula.
    - t60_eyring: Calculate T60 using the Eyring formula.
    - t60_mellington: Calculate T60 using the Mellington formula.
    - t60_csn730525: Calculate T60 using the CSN 730525 standard.
"""

from pandas import DataFrame, Series
import numpy as np

def calc_alpha_mean(
        absorption: DataFrame,
        surface_sum: float
) -> Series:
    r"""
    Calculate the mean absorption coefficient.

    Parameters
    ----------
    absorption : DataFrame
        Absorption data for different frequencies.
    surface_sum : float
        Total surface area of the room [m²].

    Returns
    -------
    Series
        Mean absorption coefficient for each frequency.

    Equation
    --------
    $$
    \alpha_{\text{mean}} = \frac{\sum \alpha}{S}
    $$
    where:
    - $\alpha_{\text{mean}}$ is the mean absorption coefficient
    - $\sum \alpha$ is the sum of absorption coefficients
    - $S$ is the total surface area [m²]
    """
    return absorption.sum() / surface_sum

def t60_sabine(
        absorption: DataFrame,
        volume: float,
        constant: float = 0.163
) -> Series:
    r"""
    Calculate T60 using the Sabine formula.

    Parameters
    ----------
    absorption : DataFrame
        Absorption data for different frequencies.
    volume : float
        Volume of the room [m³].
    constant : float, optional
        Sabine constant, default is 0.163.

    Returns
    -------
    Series
        T60 for each frequency [s].

    Equation
    --------
    $$
    T_{60} = \frac{0.163 \cdot V}{\sum \alpha}
    $$
    where:
    - $T_{60}$ is the reverberation time [s]
    - $V$ is the volume of the room [m³]
    - $\sum \alpha$ is the sum of absorption coefficients
    """
    t60 = constant * volume / absorption.sum()
    return t60

def t60_eyring(
        absorption: DataFrame,
        volume: float,
        surface_sum: float,
        constant: float = 0.163
) -> Series:
    r"""
    Calculate T60 using the Eyring formula.

    Parameters
    ----------
    absorption : DataFrame
        Absorption data for different frequencies.
    volume : float
        Volume of the room [m³].
    surface_sum : float
        Total surface area [m²].
    constant : float, optional
        Eyring constant, default is 0.163.

    Returns
    -------
    Series
        T60 for each frequency [s].

    Equation
    --------
    $$
    T_{60} = \frac{0.163 \cdot V}{-S \cdot \ln(1 - \alpha_{\text{mean}})}
    $$
    where:
    - $T_{60}$ is the reverberation time [s]
    - $V$ is the volume of the room [m³]
    - $S$ is the total surface area [m²]
    - $\alpha_{\text{mean}}$ is the mean absorption coefficient
    """
    alpha_mean = calc_alpha_mean(absorption, surface_sum)
    t60 = constant * volume / (- surface_sum * np.log(1 - alpha_mean))
    return t60

def t60_mellington(
        absorption: DataFrame,
        volume: float,
        surface_sum: float,
        attenuation: Series,
        constant: float = 0.163
) -> Series:
    r"""
    Calculate T60 using the Mellington formula.

    Parameters
    ----------
    absorption : DataFrame
        Absorption data for different frequencies.
    volume : float
        Volume of the room [m³].
    surface_sum : float
        Total surface area [m²].
    attenuation : Series
        Attenuation data for different frequencies.
    constant : float, optional
        Mellington constant, default is 0.163.

    Returns
    -------
    Series
        T60 for each frequency [s].

    Equation
    --------
    $$
    T_{60} = \frac{0.163 \cdot V}{-S \cdot \ln(1 - \alpha_{\text{mean}}) - 4 \cdot \text{attenuation} \cdot V}
    $$
    where:
    - $T_{60}$ is the reverberation time [s]
    - $V$ is the volume of the room [m³]
    - $S$ is the total surface area [m²]
    - $\alpha_{\text{mean}}$ is the mean absorption coefficient
    - $\text{attenuation}$ is the attenuation data
    """
    alpha_mean = calc_alpha_mean(absorption, surface_sum)
    t60 = constant * volume / (
            - surface_sum * np.log(1 - alpha_mean) - 4 * attenuation * volume
    )
    return t60

def t60_csn730525(
        absorption: DataFrame,
        volume: float,
        surface_sum: float,
        attenuation: Series,
        constant: float = 0.163
) -> Series:
    r"""
    Calculate T60 using the CSN 730525 standard.

    Parameters
    ----------
    absorption : DataFrame
        Absorption data for different frequencies.
    volume : float
        Volume of the room [m³].
    surface_sum : float
        Total surface area [m²].
    attenuation : Series
        Attenuation data for different frequencies.
    constant : float, optional
        CSN 730525 constant, default is 0.163.

    Returns
    -------
    Series
        T60 for each frequency [s].

    The method uses different formulas based on the mean absorption coefficient and volume:
    - Sabine formula if $\alpha_{\text{mean}} < 0.2$ and $V < 2000$ m³
    - Eyring formula if $0.2 < \alpha_{\text{mean}} < 0.8$ and $V < 2000$ m³
    - Mellington formula otherwise
    """
    alpha_mean = calc_alpha_mean(absorption, surface_sum)

    if alpha_mean.any() < 0.2 and volume < 2000:
        t60 = t60_sabine(absorption, volume, constant)
    elif 0.8 > alpha_mean.any() > 0.2 and volume < 2000:
        t60 = t60_eyring(absorption, volume, surface_sum, constant)
    else:
        t60 = t60_mellington(absorption, volume, surface_sum, attenuation, constant)
    return t60