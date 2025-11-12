
dataframe_info = """
- `name` : Name of the defect, naming conventions described below.
- `charge` : Defect charge.
- `multiplicity` : Multiplicity in the unit cell.
- `energy_diff` : Energy of the defective cell minus the energy of the pristine cell in eV.
- `bulk_volume` : Pristine cell volume in $\\mathrm{\\AA^3}$

Defect naming: (element = $A$)
- Vacancy: `'Vac_A'` (symbol=$V_{A}$)
- Interstitial: `'Int_A'` (symbol=$A_{i}$)
- Substitution: `'Sub_B_on_A'` (symbol=$B_{A}$)
- Polaron: `'Pol_A'` (symbol=${A}_{A}$)
- DefectComplex: `'Vac_A;Int_A'` (symbol=$V_A - A_i$)
"""

file_loader_info = f"""
Load session file (`.defermi`) or dataset file (`.csv`,`.pkl` or `.json`)  

`defermi`:Restore previous saved session\n
`json`: Exported `DefectsAnalysis` object from the `python` library, not generated manually\n
`csv` or `pkl`: Rows are defect entries, columns are:
{dataframe_info}
"""

band_gap_info = """
Band gap and valence band maximum of the pristine material in eV. 
"""

dataset_info = f"""
Dataset containing defect entries (`pandas.DataFrame`).\n
Toggle **Include** to add or remove the defect entry from the calculations.\n
Rows are defect entries, columns are:\n
{dataframe_info}\n

Options:
- **Edit**: enter editing mode.
- **Reset**: restore the original dataset.
- **Save csv**: Save customized dataset as `csv` file.
"""

chempots_info = """
Chemical potential of the elements that are exchanged with a reservoirs when defects are formed.\n

Formation energies depend on the chemical potentials as:\n
$$ \\Delta E_f = E_D - E_B + q(\\epsilon_{VBM} + \\epsilon_F) - \\color{blue} \\sum_i \\Delta n_i \\mu_i $$ \n

where $\\Delta n_i$ is the number of particles in the defective cell minus the number in the pristine cell for species $i$.\n

Chemical potentials can also be pulled from the Materials Project database, click **Materials Project Database**
to open the window. If **Reference composition** is left empty, chemical potentials relative to the elemental phases 
are pulled. If a compostition is specified, the phase diagram relative to the components in the target phase is retrieved,
and a dialog will appear to select which element and which condition should be used as reference.
"""

quenching_info = """
Run simulations in quenching conditions.\n
Defect concentrations are computed in charge neutral conditions at the input **Temperature(K)**,
but charges are equilibrated at **Quench Temperature (K)**. This simulates conditions where defect mobility is 
low and the high-temperature defect distribution is frozen in at low temperature.

**Quenching mode** options:
- **species**: Fix concentrations of defect species (identified by `name`).
- **elements**: Fix concentrations of elements, concentrations of individual 
                species containing the quenched elements are computed according 
                to the relative formation energies. Vacancies are considered 
                separate elements.

Select which species or elements to quench with **Select quenched species**. Defects not in the quenching list
are equilibrated at **Quench Temperature**.
"""

external_defects_info = """
Extrinsic defects contributing to charge neutrality that are NOT present in defect entries. 
They are considered in the Brouwer diagram and doping diagram calculations. \n
There is no requirement for the defect name, if a name fits one of the naming conventions,
the corrisponding symbol will be printed.
"""

cache_info = """
To prevent excessive lag when changing paramenters, the calculation result is cached. 
To rerun the calculation and regenerate the plot, click **Compute**.
"""

names_info = """
Select which defect entries to display in the plot based on `name`.
"""

concentrations_mode_info = """
Select style to plot concentrations and filter display of defect entries by `name`.

Options:
- **total**: Show the sum of concentrations in all charge states for each defect species.
- **stable**: Show the concentration of the most stable charge state for each defect species.
- **all**: Show the concentrations of all charge states for all defect species.
            Filter which charge states to show by typing them in the textbox.
"""