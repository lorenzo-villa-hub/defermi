#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 15:40:26 2020

@author: villa
"""

import numpy as np
import os
import os.path as op
import json
from monty.json import jsanitize,MontyEncoder, MontyDecoder


def get_object_feature(obj,feature):
    """
    Get value of attribute or method of a generic Object.
    If feature is a single method only the string with the method's name is required.
    If the target feature is stored in a dictionary (or dict of dictionaries), a list of
    this format needs to be provided: ["method_name",key1,key2,...]. 
        
    This will identify the value of Object.method[key1][key2][...] .

    Parameters
    ----------
    obj : object
        Generic object.
    feature : str or list
        Method or attribute of class for which the value is needed.
    
    Returns
    -------
    Object feature.

    """
    if isinstance(feature,list):
        method = feature[0]
        try:
            attr = getattr(obj,method) ()
        except:
            attr = getattr(obj,method)                
        for k in feature[1:]:
            try:
                v = attr[k]
            except:
                v = None
            if isinstance(v,dict):
                if feature.index(k) + 1 == len(feature):
                    return v
                else:
                    attr = v
            else:
                return v
            
    else:
        met = feature
        try:
            attr = getattr(obj,met) ()
        except:
            attr = getattr(obj,met)
        return attr


def decode_object_from_json(path_or_string):
    """
    Build MSONable object from json file or string.

    Parameters
    ----------
    path_or_string : str
        If an existing path to a file is given the object is constructed reading the json file.
        Otherwise it will be read as a string.

    Returns
    -------
    Decoded object.

    """
    if op.isfile(path_or_string):
        with open(path_or_string) as file:
            return MontyDecoder().decode(file.read())
    else:
        return MontyDecoder().decode(path_or_string)


def get_object_from_json(object_class,path_or_string):
    """
    Build class object from json file or string. The class must posses the 'from_dict' method.

    Parameters
    ----------
    object_class : class
        Class of the object to decode.
    path_or_string : str
        If an existing path to a file is given the object is constructed reading the json file.
        Otherwise it will be read as a string.

    Returns
    -------
    Decoded object.

    """
    if op.isfile(path_or_string):
        with open(path_or_string) as file:
            d = json.load(file)
    else:
        d = json.loads(path_or_string)

    return object_class.from_dict(d)


def save_object_as_json(object,path,sanitize=False,cls=MontyEncoder):
    """
    Save class object as json string or file. The class must posses the `as_dict` method.

    Parameters
    ----------
    object: object
        Generic object. Must posses the `as_dict` method.
    path : str
        Path to the destination file.  If None a string is exported.

    Returns
    -------
    d : str
        If path is not set a string is returned.

    """
    d = object.as_dict()
    if sanitize:
        d = jsanitize(d)
    if path:
        with open(path,'w') as file:
            json.dump(d,file,cls=cls)
        return
    else:
        return json.dumps(d,cls=cls) 


def select_objects(objects,mode='and',exclude=False,functions=None,**kwargs):
    """
    Select objects from a list based on different criteria. Returns a list of objects.

    Parameters
    ----------
    objects : list
        List of objects.
    mode : str
        Filtering mode, possibilities are: 'and' and 'or'. The default is 'and'. 
    exclude : bool
        Exclude the entries satisfying the criteria instead of selecting them. The default is False.
    functions : list
        Functions containing criteria. The functions must take the object as the argument and
        return a bool. 
    kwargs : dict
        Keys are methods/attributes the objects have. Values contain the criteria. 
        To address more than one condition relative to the same attribute,
        use lists or tuples (e.g. charge=[0,1]).

    Returns
    -------
    output_objects : list
        List with selected objects.

    """    
    selected_objects = []
    entered_selection = False
    filtered_objects = objects.copy()
    if functions:
        for func in functions:
            if func:
                entered_selection = True
                if mode=='and':
                    if selected_objects:
                        filtered_objects = selected_objects.copy()
                        selected_objects = []
                for obj in filtered_objects:
                    if func(obj) == True:
                        if obj not in selected_objects:
                            selected_objects.append(obj)
    
    for key in kwargs:
        if mode=='and':
            if selected_objects or entered_selection is True:
                filtered_objects = selected_objects.copy()
                selected_objects = []
        for obj in filtered_objects:
            feature = get_object_feature(obj,key)
            if type(kwargs[key]) in [list,tuple]:
                for value in kwargs[key]:
                    if feature == value:
                        if obj not in selected_objects:
                            selected_objects.append(obj)
            elif feature == kwargs[key]:
                if obj not in selected_objects:
                    selected_objects.append(obj)  

    if not functions and not kwargs:
        output_objects = filtered_objects
    else:
        output_objects = []
        for obj in objects:
            if exclude:
                if obj not in selected_objects:
                    output_objects.append(obj)
            else:
                if obj in selected_objects:
                    output_objects.append(obj)    
        
    return output_objects



def sort_objects(objects,features,reverse=False):
    """
    Sort objects based on a list of features (attributes or methods of the objects, or functions)

    Parameters
    ----------
    objects : list
        List of objects to sort.
    features : list
        List of features to sort by. 
        Can be a function that takes the object as argument or an attribute (see get_object_feature).
    reverse : bool
        Reverse order.

    Returns
    -------
    sorted_objects : list
        Sorted objects.

    """
    def criteria(obj):
        criteria = []
        for feature in features:
            if callable(feature):
                criteria.append(feature(obj))
            else:
                criteria.append(get_object_feature(obj,feature))
        return criteria
    sort_function = lambda obj : criteria(obj)
    sorted_objects = sorted(objects,key=sort_function,reverse=reverse)
    
    return sorted_objects


from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition

def convert_conc_from_weight_to_cm3(c_weight,target_el,composition,bulk_volume=None,bulk_structure=None):
    """
    Convert concentration of dopand from weight % (common experimental data) to cm^-3.

    Parameters
    ----------
    c_weight : float
        Defect concentration in weight %.
    target_el : str
        Symbol of target element.
    composition : Composition
        Composition of the material, uses only list of elements.
    bulk_volume : float
        Volume of bulk cell in A°^3.
    bulk_structure : Structure
        If `bulk_volume` is not provided, use the Structure object of
        bulk material to optain the cell volume.
    
    Returns
    -------
    conc : float
        Concentration in cm-3^.

    """
    if type(composition) == str:
        composition = Composition(composition)

    if not bulk_volume and not bulk_structure:
        raise ValueError('You must provide either bulk_volume or bulk_structure')
    
    sum_MM = sum([el.atomic_mass for el in composition.elements])
    r_MM = Element(target_el).atomic_mass / sum_MM
    bulk_volume = bulk_volume or bulk_structure.lattice.volume
    conc = c_weight/r_MM * 1/bulk_volume * 1e24 *0.01
    return conc


def format_composition(string,all_math=False):
    """
    Format composition with latex syntax.
    """    
    def write(newc,new_string,skip,all_math):
        if not skip:
            if all_math:
                    new_string.append('_{%s}'%newc)
            else:
                new_string.append('$_{%s}$'%newc)
        return new_string
            
    skip = False
    new_string = []
    if all_math:
        new_string.append('$')
    sp = list(string)
    
    for c in sp:        
        if c.isdigit():
            try:
                nextc = sp[sp.index(c)+1]
            except:
                nextc = ''
            if nextc.isdigit():
                newc = c + nextc
                new_string = write(newc,new_string,skip,all_math)
                skip = True
            else:
                newc = c
                new_string = write(newc,new_string,skip,all_math)
                skip = False
        else:
            new_string.append(c)
    if all_math:
        new_string.append('$')       
    new_string = ''.join(new_string)
    
    return new_string


def get_charge_from_computed_entry(entry):
    """
    Get charge of vasp calculation from ComputedEntry object. 
    Subtracts the total valence electrons from potcar to 'NELECT' value
    """
    from pymatgen.io.vasp.inputs import Potcar

    potcar_symbols_bulk = [d['titel'].split(' ')[1] for d in entry.parameters['potcar_spec']]
    potcar = Potcar(potcar_symbols_bulk)
    charge = 0
    if 'parameters' in entry.data.keys():
        parameters = entry.data['parameters']
    else:
        raise ValueError('"parameters" need to be present in ComputedEntry data')
    if 'NELECT' in parameters.keys():
        nelect = parameters['NELECT']
        val = {}
        for p in potcar:
            val[p.element] = p.nelectrons
        neutral = sum([ val[el.symbol]*coeff 
                       for el,coeff in entry.structure.composition.items()])
        charge = neutral - nelect
    if not isinstance(charge,int):
        charge = np.around(charge,decimals=1)
        
    return charge