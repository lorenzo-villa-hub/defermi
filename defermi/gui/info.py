
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

dos_info = """
Parameters for the calculation of electrons and holes concentration. Possible choices are:\n
$\\mathbf{m*/m_e}$: Effective masses of electrons (e) and holes relative to the electron mass.\n
**DOS**: Computed density of states of the pristine material. Format is either a dictionary:
- `'energies'` : list or np.array with energy values
- `'densities'` : list or np.array with total density values
- `'structure'` : pymatgen `Structure` of the material, needed for DOS volume and charge normalization

-- Alternatively, a pymatgen `Dos` object (`Dos`, `CompleteDos`, or `FermiDos`) exported as `json`.
Click on **Database** and enter the desired composition to pull the `CompleteDos` object from the 
Materials Project Database.
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

oxygen_ref_info = """
$\\mu_O(0K,p^0)$ is the chemical potential of oxygen at $T = 0 K$ and standard pressure $p^0$.\n

The oxygen partial pressure for the Brouwer diagrams is connected to the chemical potential of oxygen as:\n
$$\\mu_O(T,p_{O_2}) = \\mu_O(T,p^0) + (1/2) k_B T \\; \\mathrm{ln} (p_{O_2} / p^0) $$

where:
$$\\mu_O(T,p^0) = \\mu_O (0 K,p^0) + \\Delta \\mu_O (T,p^0) $$

The value of $\\mu_O$ in the **Chemical Potentials** section is ignored for the calculation of the Brouwer diagram.
"""

precursors_info = """
Conditions for the definition of the chemical potentials as a function of the oxygen partial pressure.
They represent the reservoirs that are in contact with the target material.\n

Each entry requires the composition and the energy per formula unit (p.f.u) in eV. Click on **Database** to pull
the energy for that composition from the Materials Project Database.\n 
Starting from the chemical potential of oxygen, the other chemical potentials are determined by the constraints 
$ E_{\\mathrm{pfu}} = \\sum_s c_s \\mu_s $, where $c_s$ are the stochiometric coefficients and $\\mu_s$ the chemical potentials.

For oxides with maximum 2 components, the target material itself is enough to determine the chemical potential of the other species.
For target oxides with more that 2 components, at least 2 compositions are needed to determine all chemical potentials.
Often these phases are chosen to be the precursors in the synthesis of the target material.\n

All elements that are not present in the entries compositions are excluded from the Brouwer diagram calculations.\n
The values in the **Chemical Potentials** section are ignored for the calculation of the Brouwer diagram.
"""

dopant_info = """
Settings for the calculation of the doping diagram.
Charge neutrality is solved varying the concentartion of a target defect. 
The chemical potentials defined in the **Chemical Potentials** section are kept fixed. \n

Options:
- **None** : Doping diagram is not computed.
- **Donor** : A generic donor is used as variable defect species. You can set the charge and concentration range.
- **Acceptor** : A generic acceptor is used as variable defect species. You can set the charge and concentration range.
- **<element>** : If extrinsic defects are present in the defect entries, 
                you can set each extrinsic element as variable defect species. Its total concentration is assigned, but the concentrations  
                of individual defects containing the element depend on the relative formation energies. 
- **custom** : Customizable dopant. You can set name, charge and concentration range. 
                There is no requirement for the defect name, if a name fits one of the naming conventions,
                the corrisponding symbol will be printed.
""" 

brouwer_diagram_info = """
Diagram of the defect concentrations as a function of the oxygen partial pressure.
Useful to compare with experiments where the oxygen partial pressure can be controlled.
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


title = """
<svg
   width="137.35327mm"
   height="26.927582mm"
   viewBox="0 0 137.35327 26.927582"
   version="1.1"
   id="svg5"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <defs
     id="defs2" />
  <g
     id="layer1"
     transform="translate(-35.33694,-51.548845)">
    <g
       aria-label="defermi"
       id="text113"
       style="font-size:37.7137px;line-height:125%;font-family:'Latin Modern Sans Quotation';-inkscape-font-specification:'Latin Modern Sans Quotation, Normal';letter-spacing:0px;word-spacing:0px;stroke-width:0.942845px">
      <path
         d="M 53.062378,76.439886 V 53.585384 c 0,-0.754274 0,-1.659402 -1.470834,-1.659402 -1.470834,0 -1.470834,0.905128 -1.470834,1.659402 v 7.54274 c -1.508548,-2.074253 -3.507374,-3.054809 -5.694769,-3.054809 -4.78964,0 -9.089001,4.337075 -9.089001,10.220412 0,5.732482 3.997652,10.182699 8.711864,10.182699 3.05481,0 4.978208,-1.961112 5.996478,-3.507374 v 1.470834 c 0,0.791988 0,1.659403 1.508548,1.659403 1.508548,0 1.508548,-0.867415 1.508548,-1.659403 z m -3.017096,-4.902781 c 0,1.169125 -0.678846,2.225109 -1.546261,3.05481 -0.791988,0.791988 -1.847972,1.508548 -3.469661,1.508548 -3.092523,0 -6.675325,-2.225108 -6.675325,-7.806736 0,-5.619341 3.884512,-7.844449 7.165603,-7.844449 1.961113,0 3.281092,1.093697 4.035366,2.225108 0.490278,0.678846 0.490278,0.791988 0.490278,1.470834 z"
         style="fill:#000080"
         id="path167" />
      <path
         d="m 76.407158,67.275457 c 0,-5.430772 -3.05481,-9.390711 -8.372441,-9.390711 -5.242204,0 -9.315284,4.676499 -9.315284,10.258126 0,5.770196 4.48793,10.333554 9.956417,10.333554 2.149681,0 4.450216,-0.641133 6.411329,-1.998826 1.131411,-0.791988 1.131411,-0.942843 1.131411,-1.244552 0,-0.754274 0,-1.923399 -0.641133,-1.923399 -0.226282,0 -0.377137,0.150855 -0.641133,0.377137 -1.961113,1.772544 -4.374789,2.413677 -6.222761,2.413677 -3.922224,0 -6.901607,-3.394233 -7.127889,-7.278744 h 13.162081 c 0.791988,0 1.659403,0 1.659403,-1.546262 z m -2.45139,-0.301709 h -12.33238 c 0.490278,-3.959939 3.281092,-6.713039 6.411329,-6.713039 5.581627,0 5.845623,5.468487 5.921051,6.713039 z"
         style="fill:#800000"
         id="path169" />
      <path
         d="m 94.170303,53.509957 v -0.527992 c 0,-0.980556 -0.03771,-1.01827 -1.508548,-1.244552 -1.169125,-0.188568 -2.262822,-0.188568 -2.564532,-0.188568 -3.582801,0 -7.165603,1.659402 -7.165603,5.129063 v 1.772544 h -2.14968 c -0.452565,0 -1.659403,0 -1.659403,1.169124 0,1.206839 1.169124,1.206839 1.659403,1.206839 h 2.14968 v 15.613471 c 0,0.754274 0,1.659403 1.470835,1.659403 1.470834,0 1.470834,-0.905129 1.470834,-1.659403 V 60.826415 h 3.809084 c 0.452564,0 1.659402,0 1.659402,-1.169125 0,-1.206838 -1.169124,-1.206838 -1.659402,-1.206838 h -3.884511 v -2.526818 c 0,-0.791988 0,-1.131411 1.43312,-1.621689 0.905129,-0.30171 1.810258,-0.377137 2.7531,-0.377137 0.754274,0 1.772544,0.03771 3.130237,0.490278 0.339424,0.113141 0.414851,0.150855 0.527992,0.150855 0.527992,0 0.527992,-0.490279 0.527992,-1.055984 z"
         style="fill:#800000"
         id="path171" />
      <path
         d="m 111.7826,67.275457 c 0,-5.430772 -3.05481,-9.390711 -8.37244,-9.390711 -5.242207,0 -9.315286,4.676499 -9.315286,10.258126 0,5.770196 4.48793,10.333554 9.956416,10.333554 2.14968,0 4.45022,-0.641133 6.41133,-1.998826 1.13141,-0.791988 1.13141,-0.942843 1.13141,-1.244552 0,-0.754274 0,-1.923399 -0.64113,-1.923399 -0.22628,0 -0.37714,0.150855 -0.64114,0.377137 -1.96111,1.772544 -4.37478,2.413677 -6.22276,2.413677 -3.92222,0 -6.901603,-3.394233 -7.127885,-7.278744 H 110.1232 c 0.79198,0 1.6594,0 1.6594,-1.546262 z m -2.45139,-0.301709 H 96.998829 c 0.490278,-3.959939 3.281091,-6.713039 6.411331,-6.713039 5.58162,0 5.84562,5.468487 5.92105,6.713039 z"
         style="fill:#000080"
         id="path173" />
      <path
         d="m 128.26347,59.65729 v -0.527992 c 0,-0.791988 0,-1.055983 -0.79199,-1.055983 -0.98055,0 -5.20449,0.339423 -7.61816,5.393059 h -0.0377 v -3.35652 c 0,-0.678846 0,-1.659402 -1.3954,-1.659402 -1.43312,0 -1.43312,0.942842 -1.43312,1.659402 v 16.330032 c 0,0.754274 0,1.659403 1.47083,1.659403 1.47083,0 1.47083,-0.905129 1.47083,-1.659403 v -8.108445 c 0,-4.563358 3.58281,-7.429599 7.46732,-7.618167 0.75427,-0.03771 0.86741,-0.03771 0.86741,-1.055984 z"
         style="fill:#000080"
         id="path175" />
      <path
         d="M 161.86637,76.439886 V 64.484643 c 0,-4.299361 -2.18739,-6.411328 -6.41133,-6.411328 -3.73365,0 -5.88333,2.45139 -6.86389,4.450216 -0.64113,-3.130237 -2.86624,-4.450216 -6.22276,-4.450216 -3.05481,0 -5.35534,1.621689 -6.75075,4.223934 h -0.0377 v -2.187395 c 0,-0.71656 0,-1.659402 -1.43313,-1.659402 -1.47083,0 -1.47083,0.905128 -1.47083,1.659402 v 16.330032 c 0,0.791988 0,1.659403 1.50855,1.659403 1.50855,0 1.50855,-0.867415 1.50855,-1.659403 v -9.767848 c 0,-3.545088 2.30053,-6.22276 5.5062,-6.22276 4.07308,0 4.56335,2.187394 4.56335,4.299361 v 11.691247 c 0,0.791988 0,1.659403 1.50855,1.659403 1.50855,0 1.50855,-0.867415 1.50855,-1.659403 v -9.767848 c 0,-3.545088 2.30054,-6.22276 5.5062,-6.22276 4.07308,0 4.56336,2.187394 4.56336,4.299361 v 11.691247 c 0,0.791988 0,1.659403 1.50855,1.659403 1.50854,0 1.50854,-0.867415 1.50854,-1.659403 z"
         style="fill:#000080"
         id="path177" />
      <path
         d="M 172.27536,76.439886 V 60.109854 c 0,-0.754274 0,-1.659402 -1.47083,-1.659402 -1.47084,0 -1.47084,0.905128 -1.47084,1.659402 v 16.330032 c 0,0.754274 0,1.659403 1.47084,1.659403 1.47083,0 1.47083,-0.905129 1.47083,-1.659403 z m 0.41485,-22.741361 c 0,-1.621689 -0.86741,-1.621689 -1.6594,-1.621689 h -0.37714 c -0.79199,0 -1.6594,0 -1.6594,1.621689 0,1.508548 0.64113,1.659403 1.69712,1.659403 h 0.30171 c 1.05598,0 1.69711,-0.150855 1.69711,-1.659403 z"
         style="fill:#000080"
         id="path179" />
    </g>
  </g>
</svg>
"""