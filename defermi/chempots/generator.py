
import numpy as np
import warnings

from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition
from pymatgen.analysis.phase_diagram import PhaseDiagram

from .core import Chempots
from .oxygen import get_pressure_reservoirs_from_precursors
from .phase_diagram import _get_composition_object, PDHandler
from .reservoirs import Reservoirs


def generate_chempots_from_condition(
                                composition,
                                condition,
                                phase_diagram=None,
                                API_KEY=None,
                                thermo_type='GGA_GGA+U',
                                **kwargs):
    """
    Generate Chempots dictionary using the data from the Materials Project. 
    Condition must be specified as "<el>-rich" or "<el>-poor".
    The phase diagram with the elements contained in the target composition is build and
    used to create the chemical potentials range for the target element.

    Parameters
    ----------
    composition : str or Composition
        Composition of the target material.
    condition : str
        Condition for the choice of chemical potential. "<el>-poor" or "<el>-rich>".
    phase_diagram : PhaseDiagram
        Pymatgen PhaseDiagram object. If not provided it is pulled from the Materials Project database.
    API_KEY : str
        API KEY for the Materials Project database. If not provided, `pymatgen` looks 
        in the configuration file.
    thermo_type : str
        The thermo type to pass to MP database. 
    kwargs : dict
        Kwargs to pass to `get_phase_diagram_from_chemsys`.

    Returns
    -------
    Chempots object

    """
    from ..tools.materials_project import MPDatabase

    comp = _get_composition_object(composition)
    if type(phase_diagram) == PhaseDiagram:
        pd = phase_diagram
    else:
        chemsys = '-'.join(el.symbol for el in comp.elements)
        pd = MPDatabase(API_KEY=API_KEY).get_phase_diagram_from_chemsys(
                                                        chemsys=chemsys,
                                                        thermo_type=thermo_type,
                                                        **kwargs)
    
    stable_compositions = [entry.composition.get_reduced_composition_and_factor()[0] for entry in pd.stable_entries]
    if comp not in stable_compositions:
        raise ValueError(f'No entry with composition={comp} is stable in phase diagram pulled from Materials Project')

    element, cond = condition.split('-')
    chempots_ranges = pd.get_chempot_range_stability_phase(target_comp=comp,open_elt=Element(element))
    if cond == 'poor':
        index = 0
    elif cond == 'rich':
        index = 1
    elif cond == 'middle':
        pass
    else:
        raise ValueError('Condition needs to be specified as "<el>-rich/poor"')
    
    chempots = {}
    for element, mus in chempots_ranges.items():
        if cond == 'middle':
            chempots[element.symbol] = float(np.mean(mus))
        else:
            chempots[element.symbol] = float(mus[index])


    return Chempots(chempots)


def generate_chempots_from_mp(
                            composition,
                            element=None,
                            phase_diagram=None,
                            API_KEY=None,
                            thermo_type='GGA_GGA+U',
                            **kwargs):
    """
    Generate Chempots dictionary using the data from the Materials Project. 
    `element` can be a periodic table element, or a condition "<el>-poor/rich"
    (see docs in `generate_chempots_from_condition`).
    If not provided, oxygen is chosen as target element if present,
    otherwise the last element in the composition formula is picked.

    If `element` is provided as condition ("<el>-poor/rich"), a `Chempots` object is
    returned, otherwise all conditions are pulled from the database and a `Reservoirs`
    object is returned (a `Chempots` object for every condition).

    Parameters
    ----------
    composition : str or Composition
        Composition of the target material.
    element : str
        Periodic table element or condition ("<el>-poor/rich") for the choice of chemical potential.
        if a condition is provided, a `Chempots` object is
        returned, otherwise all conditions are pulled from the database and a `Reservoirs`
        object is returned (a `Chempots` object for every condition).
    phase_diagram : PhaseDiagram
        Pymatgen PhaseDiagram object. If not provided it is pulled from the Materials Project database.
    API_KEY : str
        API KEY for the Materials Project database. If not provided, `pymatgen` looks 
        in the configuration file.
    thermo_type : str
        The thermo type to pass to MP database. 
    kwargs : dict
        Kwargs to pass to `get_phase_diagram_from_chemsys`.

    Returns
    -------
    chemical_potentials : Chempots or Reservoirs
        Chemical potentials for the target composition and condition.
        If `element` is provided as condition ("<el>-poor/rich"), a `Chempots` object is
        returned, otherwise all conditions are pulled from the database and a `Reservoirs`
        object is returned (a `Chempots` object for every condition).

    """
    from ..tools.materials_project import MPDatabase

    string_conditions = ['poor','middle','rich']
    print('Pulling chemical potentials from Materials Project database...')
    
    comp = _get_composition_object(composition)
    if type(phase_diagram) == PhaseDiagram:
        pd = phase_diagram
    else:
        chemsys = '-'.join(el.symbol for el in comp.elements)
        pd = MPDatabase(API_KEY=API_KEY).get_phase_diagram_from_chemsys(
                                                        chemsys=chemsys,
                                                        thermo_type=thermo_type,
                                                        **kwargs)
    if element:
        condition = element
    else:
        condition = []
        composition = Composition(composition)
        if 'O' in composition:
            element = 'O'
        else:
            element = composition.elements[-1].symbol

    if any([cond in condition for cond in string_conditions]):          
        chempots = generate_chempots_from_condition(
                                        composition=composition,
                                        condition=condition,
                                        phase_diagram=pd,
                                        API_KEY=API_KEY,
                                        thermo_type=thermo_type,
                                        **kwargs)
        chemical_potentials = Chempots(chempots)
        print(f'Chemical potentials for composition = {composition} and condition = {condition}:')
        print(chempots)

    else:
        chemical_potentials = {}
        if element in composition:
            for condition in [element +'-'+ cond for cond in string_conditions]:
                chempots = generate_chempots_from_condition(
                                        composition=composition,
                                        condition=condition,
                                        phase_diagram=pd,
                                        API_KEY=API_KEY,
                                        thermo_type=thermo_type,
                                        **kwargs)
                chemical_potentials[condition] = chempots
            chemical_potentials = Reservoirs(chemical_potentials,phase_diagram=pd)
        else:
            raise ValueError('Target element is not in composition')
        print(f'Chemical potentials:\n {chemical_potentials}')       

    return chemical_potentials 


def generate_elemental_chempots(elements, API_KEY=None, thermo_type='GGA_GGA+U', **kwargs):
    """
    Generate chemical potentials for reference elemental phases 
    using the data from the Materials Project database.

    Parameters
    ----------
    elements : list
        List of strings with element symbols.
    API_KEY : str
        API KEY for the Materials Project database. If not provided, `pymatgen` looks 
        in the configuration file.
    thermo_type : str
        The thermo type to pass to MP database. 
    kwargs : dict
        Kwargs to pass to `get_phase_diagram_from_chemsys`.

    Returns
    -------
    Chempots object

    """
    chempots = {}
    from mp_api.client import MPRester
    with MPRester(API_KEY) as mpr:
        for el in elements:
            # code adapted from .tools.materials_project.get_stable_energy_pfu_from_composition to avoid creating a new MPRester instance every time
            docs = mpr.materials.thermo.search(formula=el,energy_above_hull=(0,0),thermo_types=[thermo_type],**kwargs)
            if len(docs) > 1:
                warnings.warn('Search returned more than one entry with E above hull = 0 eV, check manually. Returning the first entry...')
            entry = docs[0]
            chempots[el] = entry.energy_per_atom
    return Chempots(chempots)


def generate_pressure_reservoirs_from_precursors(
                                            precursors,
                                            temperature,
                                            oxygen_ref=None,
                                            pressure_range=(1e-20,1e10),
                                            npoints=50,
                                            get_pressures_as_strings=False,
                                            thermo_type='GGA_GGA+U',
                                            **kwargs):
    """
    Generate reservoirs dependent on oxygen partial pressure (`PressureReservoirs`)
    starting from precursors compostitions.
    A dictionary with precursor composition and energy per formula unit in eV is generated 
    with data from the Materials Project database.
    If not provided, the reference for the oxygen chempot at 0 K is also pulled from the DB.
    Chemical potentials are found from the energies of the precursors and the oxygen chempot value 
    (uses the np.linalg.lstsq function). 
    If the system is underdetermined the minimum-norm solution is found.

    Parameters
    ----------
    precursors : str or list
        Compositions of precursors.
    oxygen_ref : float
        Absolute chempot of oxygen at 0K. If not provided it is pulled from the MP database.
    temperature : float
        Temperature in K.
    pressure_range : tuple
        Range in which to evaluate the partial pressure . The default is from 1e-20 to 1e10.
    npoints : int
        Number of data points to interpolate the partial pressure with. The default is 50.
    get_pressures_as_strings : bool
        Get pressure values (keys in the Reservoirs dict) as strings. The default is set to floats.

    Returns
    -------
    pressure_reservoirs : PressureReservoirs
        PressureReservoirs object.

    """
    from ..tools.materials_project import MPDatabase

    print('Pulling precursors energies from Materials Project database')
    if type(precursors) == str:
        precursors = [precursors]
    if not oxygen_ref:
        oxygen_ref = MPDatabase().get_stable_energy_pfu_from_composition(
                                                                composition='O2',
                                                                thermo_types=[thermo_type],
                                                                **kwargs)
        oxygen_ref /= 2       
    
    precursors_dict = {}
    for prec in precursors:
        energy_pfu = MPDatabase().get_stable_energy_pfu_from_composition(
                                                                composition=prec,
                                                                thermo_types=[thermo_type],
                                                                **kwargs)
        precursors_dict[prec] = energy_pfu

    reservoirs = get_pressure_reservoirs_from_precursors(
                                            precursors=precursors_dict,
                                            oxygen_ref=oxygen_ref,
                                            temperature=temperature,
                                            pressure_range=pressure_range,
                                            npoints=npoints,
                                            get_pressures_as_strings=get_pressures_as_strings)
    
    return reservoirs

    

