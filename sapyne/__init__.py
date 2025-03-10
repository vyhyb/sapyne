r"""# Sapyne

Sapyne is a Python package for basic room acoustics calculations. 
It provides functions to calculate the attenuation coefficient, 
absorption area, reverberation time, and (in the future) other room 
acoustics parameters. It mostly serves for room acoustic design according
to the ČSN 73 0527 standard.

## Installation

It is currently not possible to install this library using `pip` or `conda`, 
please use the latest released package instead and install using 
[`pip` locally](https://packaging.python.org/en/latest/tutorials/installing-packages/).

## Documentation

Documentation can be found [here](https://vyhyb.github.io/sapyne/).

## Usage

Will be added in the future.

## Author

- [David Jun](https://www.fce.vutbr.cz/o-fakulte/lide/david-jun-12801/)
  
  PhD student at [Brno University of Technology](https://www.vutbr.cz/en/).

## Contributing

Pull requests are welcome. For any changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

## References
- [1] ČSN 730525 -  Akustika - Projektování v oboru prostorové akustiky - Všeobecné zásady, Praha, manual, 1998.
- [2] ČSN 730526 - Akustika - Projektování v oboru prostorové akustiky - Studia a místnosti pro snímání, zpracování a kontrolu zvuku, Český normalizační institut, Praha, manual, 1998.
- [3] ČSN 730527 - Akustika - Projektování v oboru prostorové akustiky. Prostory pro kulturní a školní účely. Prostory pro veřejné účely. Administrativní pracovny, Praha, manual, 2005.
- [4] ČSN EN ISO 3382-1   (730534) - Akustika - Měření parametrů prostorové akustiky - Část 1: Prostory pro přednes hudby a řeči, manual, Praha., 2009.
- [5] ČSN EN ISO 3382-2   (730534) - Akustika - Měření parametrů prostorové akustiky - Část 2: Doba dozvuku v běžných prostorech, manual, Praha., 2009.
- [6] ISO 3382-3:2022 - Acoustics - Measurement of room acoustic parameters - Part 3: Open plan offices, Geneve., 2022. Accessed: Nov. 09, 2022. [Online]. Available: https://www.iso.org/standard/77437.html
- [7] ISO 354:2003 Acoustics - Measurement of sound absorption in a reverberation room, Geneva, Switzerland., May 2003. [Online]. Available: https://www.iso.org/standard/34545.html
- [8] ISO 9613-1:1993 - Acoustics - Attenuation of sound during propagation outdoors - Part 1: Calculation of the absorption of sound by the atmosphere, Geneve., 1993.

"""
from .attenuation import attenuation_coefficient
from .experimental_absorption import eq_absorption_area, absorption_coeff_ISO_354
from .models import t60_sabine, t60_eyring, t60_mellington, t60_csn730525
from .models import calc_alpha_mean
from .standard import ROOM_TYPES
from .rt_imports import DiracReverberationData, REWReverberationData, REW_QUANTITIES, merge_rew_dfs

