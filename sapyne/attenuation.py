"""Sound attenuation in air
"""
import numpy as np
from pandas import Series

def attenuation_coefficient(
    frequency: float|np.ndarray|Series,
    relative_humidity: float,
    temperature: float,
    pressure: float,
    norm_pressure = 101.325,
    temp_ref = 293.15
    ) -> Series:
    r"""
    Calculate the sound attenuation coefficient in air based on the given criteria.
    According to ISO 9613-1:1993.

    Parameters
    ----------
    frequency : float|np.ndarray|Series
        Frequency bands for the calculation. [Hz]
    relative_humidity : float
        Relative humidity at the time of measurement. [%]
    temperature : float
        Air temperature at the time of measurement. [degC]
    pressure : float
        Atmospheric pressure at the time of measurement. [kPa]
    norm_pressure : float, optional
        Normal atmospheric pressure (reference). Default is 101.325.
    temperature_0 : float, optional
        Reference temperature (20 °C). Default is 293.15.    

    Returns
    -------
    att_coeff : float
        Sound attenuation coefficient.

    Notes
    -----
    The sound attenuation coefficient is calculated using the following formulas:
    $$
    C = -6.8346 \left( \frac{273.16}{T} \right)^{1.261} + 4.6151
    $$
    where:
    - $T$ is the temperature [K]
    - $T_0$ is the reference temperature [K]

    $$
    p_{sat} = p_r \cdot 10^C
    $$
    where:
    - $p_{sat}$ is the saturation pressure [kPa]
    - $p_r$ is the normal pressure [kPa]

    $$
    h = h_r \cdot \frac{p_{sat}}{p_r} \cdot \frac{p_r}{p_a}
    $$
    where:
    - $h$ is the ...
    - $h_r$ is the relative humidity [%]
    - $p_a$ is the atmospheric pressure [kPa]

    $$
    f_{rO} = \frac{p_a}{p_r} \left( 24 + 4.04 \times 10^4 \cdot 
    \frac{h \cdot (0.02 + h)}{0.391 + h} \right)
    $$
    where:
    - $f_{rO}$ is the relaxation frequency of oxygen [Hz]

    $$
    f_{rN} = \frac{p_a}{p_r} \left( \frac{T}{T_0} \right)^{-0.5} 
    \left( 9 + 280 \cdot h \cdot \exp \left( -4.170 \left( \left( 
        \frac{T}{T_0} \right)^{-1/3} - 1 
    \right) \right) \right)
    $$
    where:
    - $f_{rN}$ is the relaxation frequency of nitrogen [Hz]

    $$
    \alpha = 8.686 \cdot f^2 \left( \left( 1.84 \times 10^{-11} \cdot 
    \frac{p_r}{p_a} \cdot \left( \frac{T}{T_0} \right)^{0.5} \right) + 
    \left( \left( \frac{T}{T_0} \right)^{-5/2} 
    \left( 0.01275 \cdot \left( f_{rO} + \frac{f^2}{f_{rO}} \right)^{-1} \cdot \exp \left( -\frac{2239.1}{T} \right) 
    + 0.1068 \cdot \left( f_{rN} + \frac{f^2}{f_{rN}} \right)^{-1} \cdot \exp \left( -\frac{3352.0}{T} 
    \right) \right) \right) \right)
    $$
    where:
    - $\alpha$ is the sound attenuation coefficient [dB/m]

    $$
    m = \frac{\alpha}{10 \cdot \log_{10} e}
    $$
    where:
    - $m$ is the sound attenuation coefficient used in the ISO 354 and ISO 3382 standards [m⁻¹]
    """

    f = frequency

    T = temperature + 273.15
    T_0 = temp_ref
    
    p_r = norm_pressure
    p_a = pressure
    h_r = relative_humidity
    C = -6.8346 * (273.16 / T) ** 1.261 + 4.6151
    p_sat = p_r * 10 ** C
    h = h_r * (p_sat / p_r) / (p_a / p_r)
    
    f_rO = p_a / p_r * (24 + 4.04e4 * h * (0.02 + h)/(0.391 + h))

    f_rN = p_a / p_r * (T / T_0) ** (-0.5) * (
        9 + 280 * h * np.exp(-4.170 * ((T / T_0) ** (-1/3) - 1))
        )

    att_coeff = 8.686 * f ** 2 * (
        (1.84e-11 * (p_r / p_a) * (T / T_0) ** 0.5)
        + (T / T_0) ** (-5/2)
        * (0.01275 * (f_rO + f ** 2 / f_rO) ** (-1) * np.exp(-2239.1 / T)
        + 0.1068 * (f_rN + f ** 2 / f_rN) ** (-1) * np.exp(-3352.0 / T))
        )
    print(att_coeff)

    att_coeff = att_coeff / (10 * np.log10(np.exp(1)))
    return att_coeff