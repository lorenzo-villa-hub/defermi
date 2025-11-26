
<p align="center">
    <img src="./images/defermi_logo.png" alt="logo" width="400"/>
</p>

[![](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/lorenzo-villa-hub/defermi)
[![PyPI](https://img.shields.io/pypi/v/defermi)](https://pypi.org/project/defermi/)

Python library for the analysis and visualization of point defects. Simple and intuitive for new users and non-experts, flexible and customizable for power users. An intuitive user interface can be run online with no installation at this link: https://defermi.streamlit.app/ (using [streamlit](https:/streamlit.io)).  \


## Installation

If you are using `conda` or `mamba`, creating a new environment is recommended:
```python
mamba create env -n defermi python
mamba activate defermi
```

The package can be installed with PyPI:
```python
pip install defermi
```

## UI
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://defermi.streamlit.app/) 
[![](https://img.shields.io/badge/github-repo-blue?logo=github)](https://github.com/lorenzo-villa-hub/defermi-gui)
[![PyPI](https://img.shields.io/pypi/v/defermi)](https://pypi.org/project/defermi-gui/)

The library comes with a simple and intutitive graphical user interface. It runs in the brouwser without installation on this link:\
https://defermi.streamlit.app/

<p align="center">
    <img src="./images/defermi_main_screenshot.png" alt="logo" width="700"/>
</p>

It can also be run locally. Install it first:
```bash
pip install defermi-gui
```
and run it with:
```bash
defermi-gui
```

## Features 

- **Formation energies**: Easily calculate and plot formation energies of point defects.
- **Charge transition levels** : Compute and visualize defect thermodynamic transition levels.
- **Chemical potentials** : Generate, analyse and visualize datasets of chemical potentials. Automated workflow for datasets generations based on oxygen partial pressures. 
- **Defect complexes** : Support for defect complexes is included. 
- **Equilibrium Fermi level** : Compute the Fermi level dictated by charge neutrality self-consistently.
- **Brouwer and doping diagrams** : Automatic generation of Brouwer diagrams and doping diagrams.
- **Temperature-dependent formation energies and defect concentrations** : System-specific temperature-dependence of formation energies and defect concentartions can be included and customized.
- **Extended frozen defects approach** : Calculate Fermi level under non-equilibrium conditions. Fix defect concentrations to a target value while allowing the charge to equilibrate. This approach is extremely useful for the simulation of quenched conditions, when the defect distribution is determined at high temperature and frozen in at low temperature, or when extrinsic defects are present and the charge state depends on the Fermi level. This approach has been extended to different defects containing the same element and to defect complexes. Many options regarding the fixing conditions are available, including partial quenching and elemental concentrations.
- **Finite-size corrections**: Compute charge corrections (FNV and eFNV schemes). At the moment available for `VASP` calculations using `pymatgen`.
- **Automatic import from `VASP` calculations** : Import dataset directly from your `VASP` calculation directory. Support for`gpaw` will soon be included.

## Overview
- **Intuitive** : No endless reading of the documentation, all main functionalities are wrapped around the `DefectsAnalysis` class.
- **Easy interface** : Interfaces with simple Python objects (`list`,`dict`,`DataFrame`), no unnecessary dependencies on specific objects. Fast learning curve: getting started is as simple as loading a `DataFrame` or a `csv` file.
- **Flexible** : Power users can customize the workflow and are not limited by the default behaviour. All individual routines are easily accessible manually to improve control.
- **Customizable** : Users can assign their own customized functions for defect formation energies and concentrations. Not only temperature and volume dependences can be easily included, but also system-specific behaviours can be integrated without the need for workarounds. 



## Quick-start

The central class of the library is `DefectsAnalysis`. The most flexible way to initialize it is using a `pandas.DataFrame`. Columns are:
- `name` : Name of the defect, naming conventions described below.
- `charge` : Defect charge.
- `multiplicity` : Multiplicity in the unit cell.
- `energy_diff` : Energy of the defective cell minus the energy of the pristine cell in eV.
- `bulk_volume` : Pristine cell volume in $\mathrm{\AA^3}$

Defect naming: (element = $A$)
- `Vacancy`: `"Vac_A"` (symbol=$V_{A}$)
- `Interstitial`: `"Int_A"` (symbol=$A_{i}$)
- `Substitution`: `"Sub_B_on_A"` (symbol=$B_{A}$)
- `Polaron`: `"Pol_A"` (symbol=${A}_{A}$)
- `DefectComplex`: `"Vac_A;Int_A"` (symbol=$V_{A}-A_{i}$)

Let's create an example `DataFrame` with <span style="color:red"> made-up energies </span> as an example. We are studying $SrO$ and have energies for the neutral and charged $Sr$ and $O$ vacancies.


```python
import pandas as pd
from defermi import DefectsAnalysis

bulk_volume = 800 # cubic Amstrong
data = [
{'name': 'Vac_O','charge': 2,'multiplicity': 1,'energy_diff': 7,'bulk_volume': bulk_volume},
{'name': 'Vac_O','charge':0,'multiplicity':1,'energy_diff': 10.8, 'bulk_volume': bulk_volume},
{'name': 'Vac_Sr','charge': -2,'multiplicity': 1,'energy_diff': 8,'bulk_volume': bulk_volume},
{'name': 'Vac_Sr','charge': 0,'multiplicity': 1,'energy_diff': 7.8,'bulk_volume': bulk_volume},
]
df = pd.DataFrame(data)
df
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>charge</th>
      <th>multiplicity</th>
      <th>energy_diff</th>
      <th>bulk_volume</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Vac_O</td>
      <td>2</td>
      <td>1</td>
      <td>7.0</td>
      <td>800</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Vac_O</td>
      <td>0</td>
      <td>1</td>
      <td>10.8</td>
      <td>800</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Vac_Sr</td>
      <td>-2</td>
      <td>1</td>
      <td>8.0</td>
      <td>800</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Vac_Sr</td>
      <td>0</td>
      <td>1</td>
      <td>7.8</td>
      <td>800</td>
    </tr>
  </tbody>
</table>
</div>

```python
# Initialize DefectsAnalysis object
da = DefectsAnalysis.from_dataframe(df,band_gap=2,vbm=0) # band gap and valence band maximum in eV
```


```python
import matplotlib.pyplot as plt


chempots = {'O':-5,'Sr':-2} # Define chemical potentials for each element in a dictionary

# Plot formation energies
da.plot_formation_energies(chemical_potentials=chempots,title='Formation energies',figsize=(5,5)).show()

# Plot charge transition levels
da.plot_ctl(figsize=(4,4),fontsize=12)
plt.title('Charge transition levels');
```
    
![png](./tutorials/quick-start_files/quick-start_3_0.png)
    
![png](./tutorials/quick-start_files/quick-start_3_1.png)
    
#### Fermi level dictated by charge neutrality

`defermi` also offers an easy way to study the defect equilibrium dictated by charge neutrality in different conditions. Defect concentrations can be plotted as a function of the oxygen partial pressure (Brouwer diagram) and dopant concentration (doping diagram) with one line of code.


```python
# Brouwer diagram

precursors = {'SrO':-10} # Reservoir and energy p.f.u for the chemical potentials definition
oxygen_ref = -4.95  # chemical potential of oxygen at 0 K and standard pressure
bulk_dos = {'m_eff_e':0.5, 'm_eff_h':0.4}  # effective masses for the charge carriers calculation

da.plot_brouwer_diagram(
                    bulk_dos=bulk_dos,
                    temperature=1000, # Kelvin
                    precursors=precursors,
                    oxygen_ref=oxygen_ref,
                    pressure_range=(1e-35,1e25), # atm
                    figsize=(5,5))
plt.title('Brouwer diagram')
plt.show()

# Doping diagram

da.plot_doping_diagram(
                variable_defect_specie={'name':'Donor','charge':1},
                concentration_range=(1e11,1e20),  # cm^-3
                chemical_potentials=chempots,
                bulk_dos=bulk_dos,
                temperature=1000,  # Kelvin
                figsize=(5,5))
plt.title('Doping diagram');
```

![png](./tutorials/quick-start_files/quick-start_5_0.png)

![png](./tutorials/quick-start_files/quick-start_5_1.png)
    



