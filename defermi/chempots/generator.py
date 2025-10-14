
import numpy as np

from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition

from .core import Chempots
from .phase_diagram import _get_composition_object, PDHandler
from .reservoirs import Reservoirs


def generate_chempots_from_condition(target_composition, condition, API_KEY=None, **kwargs):
    """
    Generate Chempots dictionary using the data from the Materials Project. 
    Condition must be specified as "<el>-rich" or "<el>-poor".
    The phase diagram with the elements contained in the target composition is build and
    used to create the chemical potentials range for the target element.

    Parameters
    ----------
    target_composition : str or Composition
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

    comp = _get_composition_object(target_composition)
    chemsys = '-'.join(el.symbol for el in comp.elements)
    
    default_thermo_type = 'GGA_GGA+U'
    if kwargs: 
        if 'thermo_type' not in kwargs:
            kwargs['thermo_type'] = default_thermo_type
    else:
        kwargs = {'thermo_type':default_thermo_type}

    with MPRester(API_KEY) as mpr:
        pd = mpr.materials.thermo.get_phase_diagram_from_chemsys(chemsys=chemsys,**kwargs)
    
    target_el, cond = condition.split('-')
    chempots_ranges = pd.get_chempot_range_stability_phase(target_comp=comp,open_elt=Element(target_el))
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


def generate_chempots_from_mp(target, API_KEY=None, **kwargs):

    if type(target) in (str,tuple):
        string_conditions = ['poor','middle','rich']
        print('Pulling chemical potentials from Materials Project database...')
        if type(target) == tuple:
            if target[1] in string_conditions:
                target_composition, condition = target
            else:
                condition = []
                target_composition, target_el = target

        elif type(target) == str:
            condition = []
            target_composition = Composition(target)
            if 'O' in target_composition:
                target_el = 'O'

        if any([cond in condition for cond in string_conditions]): 
            target_composition, condition = target           
            chempots = generate_chempots_from_condition(
                                            target_composition=target_composition,
                                            condition=condition)
            chemical_potentials = chempots
            print(f'Chemical potentials for composition: {target_composition} and condition: {condition}:')
            print(chempots)

        else:
            chemical_potentials = {}
            if target_el in target_composition:
                for condition in ['O-poor','O-middle','O-rich']:
                    chempots = generate_chempots_from_condition(
                                target_composition=target_composition,
                                condition=condition)
                    chemical_potentials[condition] = chempots
            else:
                raise ValueError('Target element is not in composition')
            print(f'Chemical potentials: {chemical_potentials}')        

