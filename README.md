# defy

Python library for the analysis and visualization of point defects. Simple and intuitive for new users and non-experts, flexible and customizable for power users.


## Installation

<pre> ```pip install defy ``` </pre>

## Features 

- **Formation energies**: Easily calculate and plot formation energies of point defects.
- **Charge transition levels** : Compute and visualize defect thermodynamic transition levels.
- **Chemical potentials** : Generate, analyse and visualize datasets of chemical potentials. Automated workflow for datasets generations based on oxygen partial pressures. 
- **Defect complexes** : Support for defect complexes is included. 
- **Equilibrium Fermi level** : Compute the Fermi level dictated by charge neutrality self-consistently.
- **Brouwer and doping diagrams** : Automatic generation of Brouwer diagrams and doping diagrams.
- **Temperature-dependent formation energies and defect concentrations** : System-specific temperature-dependence of formation energies and defect concentartions can be included and customized.
- **Extended frozen defects approach** : Calculate Fermi level under non-equilibrium conditions. Fix defect concentrations to a target value while allowing the charge to equilibrate. This approach is extremely useful for the simulation of quenched conditions, when the defect distribution is determined at high temperature and frozen in at low temperature, or when extrinsic defects are present and the charge state depends on the Fermi level. This approach has been extended to different defects containing the same element and to defect complexes. Many options regarding the fixing conditions are available, including partial quenching and elemental concentrations.
- **Finite-size corrections**: Compute charge corrections (FNV and eFNV schemes). At the moment available for VASP calculations using `pymatgen`.
- **Automatic import from VASP calculations** : Import dataset directly from your VASP calculation directory. `gpaw` and `ase.db` support will soon be included.

## Overview
- **Intuitive** : No endless reading of the documentation, all main functionalities are wrapped around the `DefectsAnalysis` class.
- **Easy interface** : Interfaces with simple Python objects (`list`,`dict`,`DataFrame`), no dependency on specific objects. Fast learning curve. Getting started is as simple as loading a `DataFrame` or a `csv` file.
- **Flexible** : Power users can customize the workflow and are not limited by the default behaviour. All individual routines are easily accessible manually to improve control.
- **Customizable** - : Users can assign their own customized functions for defect formation energies and concentrations. Not only temperature and volume dependences can be easily included, but also system-specific behaviours can be integrated without the need for workarounds. 
