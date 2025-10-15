
import numpy as np

from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition

from .core import Chempots
from .phase_diagram import _get_composition_object, PDHandler
from .reservoirs import Reservoirs


def generate_chempots_from_condition(composition, condition, API_KEY=None, **kwargs):
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
    API_KEY : str
        API KEY for the Materials Project database. If not provided, `pymatgen` looks 
        in the configuration file.
    kwargs : dict
        Kwargs to pass to `get_phase_diagram_from_chemsys`.
        'thermo_type' is set by default as 'GGA_GGA+U'.

    Returns
    -------
    Chempots object

    """
    from mp_api.client import MPRester

    comp = _get_composition_object(composition)
    chemsys = '-'.join(el.symbol for el in comp.elements)
    
    default_thermo_type = 'GGA_GGA+U'
    if kwargs: 
        if 'thermo_type' not in kwargs:
            kwargs['thermo_type'] = default_thermo_type
    else:
        kwargs = {'thermo_type':default_thermo_type}

    with MPRester(API_KEY) as mpr:
        pd = mpr.materials.thermo.get_phase_diagram_from_chemsys(chemsys=chemsys,**kwargs)
    
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


def generate_chempots_from_mp(composition, element=None, API_KEY=None, **kwargs):
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
    API_KEY : str
        API KEY for the Materials Project database. If not provided, `pymatgen` looks 
        in the configuration file.
    kwargs : dict
        Kwargs to pass to `get_phase_diagram_from_chemsys`.
        'thermo_type' is set by default as 'GGA_GGA+U'.

    Returns
    -------
    chemical_potentials : Chempots or Reservoirs
        Chemical potentials for the target composition and condition.
        If `element` is provided as condition ("<el>-poor/rich"), a `Chempots` object is
        returned, otherwise all conditions are pulled from the database and a `Reservoirs`
        object is returned (a `Chempots` object for every condition).

    """

    string_conditions = ['poor','middle','rich']
    print('Pulling chemical potentials from Materials Project database...')
    if element:
        condition = element
    else:
        condition = []
        composition = Composition(composition)
        if 'O' in composition:
            element = 'O'
        else:
            composition.elements[-1].symbol

    if any([cond in condition for cond in string_conditions]):          
        chempots = generate_chempots_from_condition(
                                        composition=composition,
                                        condition=condition)
        chemical_potentials = Chempots(chempots)
        print(f'Chemical potentials for composition = {composition} and condition = {condition}:')
        print(chempots)

    else:
        chemical_potentials = {}
        if element in composition:
            for condition in [element +'-'+ cond for cond in string_conditions]:
                chempots = generate_chempots_from_condition(
                            composition=composition,
                            condition=condition)
                chemical_potentials[condition] = chempots
            chemical_potentials = Reservoirs(chemical_potentials)
        else:
            raise ValueError('Target element is not in composition')
        print(f'Chemical potentials:\n {chemical_potentials}')       

    return chemical_potentials 

