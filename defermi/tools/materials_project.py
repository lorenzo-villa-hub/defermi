#!/usr/bin/env python

import warnings




class  MPDatabase:
    
    from mp_api.client import MPRester # only import within this class

    def __init__(self,mp_id=None,API_KEY=None):
        """
        Class to retrieve data from Materials Project database

        Parameters
        ----------
        mp_id : str
            Materials-ID.
        API_KEY : str
            API_KEY for MAterials Project database. If None the default key from
            the configuration file for `pymatgen` is used.
        """
        
        self.mp_id = mp_id if mp_id else None
        self.API_KEY = API_KEY
    
    @property
    def mp_rester(self):
        return self.MPRester(self.API_KEY)
        
        
    def get_dos_from_stable_composition(self,composition,thermo_types=['GGA_GGA+U'],**kwargs):
        """
        Get the CompleteDos object of the entry with E above Convex Hull = 0 eV for a target composition. 

        Parameters
        ----------
        composition : str
            Target composition (eg. "SrTiO3").
        thermo_type : str
            Thermo types to return data for (e.g. "GGA_GGA+U").
            Check `mp_api` docs for information on thermo types.
        kwargs : dict
            Kwargs to pass to `MPRester().materials.thermo.get_phase_diagram_from_chemsys`.

        Returns
        -------
        CompleteDos

        """
        entry = self.get_stable_entry_from_composition(composition=composition,thermo_types=thermo_types,**kwargs)
        material_id = entry.material_id
        with self.MPRester(self.API_KEY) as mpr:
            dos = mpr.get_dos_by_material_id(material_id)
        return dos


    def get_entries(self,
                    chemsys_formula_mpids,
                    compatible_only=True,
                    property_data=None,
                    conventional_unit_cell=False,
                    sort_by_e_above_hull=True):
        """
        Get a list of ComputedEntries or ComputedStructureEntries corresponding
        to a chemical system, formula, or materials_id or full criteria.

        Parameters
        ----------
        chemsys_formula_id_criteria : str or dict
            A chemical system (e.g., Li-Fe-O), or formula (e.g., Fe2O3) 
            or materials_id (e.g., mp-1234) or full Mongo-style dict criteria.
        compatible_only : bool
            Whether to return only "compatible"
            entries. Compatible entries are entries that have been
            processed using the MaterialsProject2020Compatibility class,
            which performs adjustments to allow mixing of GGA and GGA+U
            calculations for more accurate phase diagrams and reaction
            energies.
        property_data : list
            Specify additional properties to include in
            entry.data. If None, no data. Should be a subset of
            supported_properties.
        conventional_unit_cell : bool
            Whether to get the standard conventional unit cell.

        Returns
        -------
        entries : list
            List of ComputedStructureEntry objects.

        """
        with self.MPRester(self.API_KEY) as mpr:
            entries = mpr.get_entries(
                                chemsys_formula_mpids=chemsys_formula_mpids,
                                compatible_only=compatible_only,
                                property_data=property_data,
                                conventional_unit_cell=conventional_unit_cell)
        return entries
    
    
    def get_entries_from_compositions(self,
                                    compositions,
                                    compatible_only=True,
                                    property_data=None,
                                    conventional_unit_cell=False):
        """
        Get a dictionary with compositions (strings) as keys and a list of ComputedEntries 
        or ComputedStructureEntries as values.

        Parameters
        ----------
        compositions : list
            List of strings with compositions.
        compatible_only : bool
            Whether to return only "compatible"
            entries. Compatible entries are entries that have been
            processed using the MaterialsProject2020Compatibility class,
            which performs adjustments to allow mixing of GGA and GGA+U
            calculations for more accurate phase diagrams and reaction
            energies.
        property_data : list
            Specify additional properties to include in
            entry.data. If None, no data. Should be a subset of
            supported_properties.
        conventional_unit_cell : bool
            Whether to get the standard conventional unit cell.

        Returns
        -------
        entries : list
            List of ComputedStructureEntry objects.

        """
        entries_dict = {}
        for comp in compositions:
            entries = self.get_entries(
                                    chemsys_formula_mpids=comp,
                                    compatible_only=compatible_only,
                                    property_data=property_data,
                                    conventional_unit_cell=conventional_unit_cell)
            entries_dict[comp] = entries
        
        return entries_dict
    

    def get_phase_diagram_from_chemsys(self,chemsys,thermo_type='GGA_GGA+U', **kwargs):
        """
        Pull `PhaseDiagram` object from MP database given a chemical system (eg. "Li-Nb-O").

        Parameters
        ----------
        chemsys : str
            Chemical system (eg. "Li-Nb-O").
        thermo_type : str
            Thermo types to return data for (e.g. "GGA_GGA+U").
            Check `mp_api` docs for information on thermo types.
        kwargs : dict
            Kwargs to pass to `MPRester().materials.thermo.get_phase_diagram_from_chemsys`.

        Returns
        -------
        pd : PhaseDiagram
            `PhaseDiagram` object.
        """
        with self.MPRester(self.API_KEY) as mpr:
            pd = mpr.materials.thermo.get_phase_diagram_from_chemsys(
                                                                chemsys=chemsys,
                                                                thermo_type=thermo_type,
                                                                **kwargs)
        return pd
    

    def get_stable_entry_from_composition(self,composition,thermo_types=['GGA_GGA+U'],**kwargs):
        """
        Pull from MP database the entry with E above Convex Hull = 0 eV for a target composition.

        Parameters
        ----------
        composition : str
            Target composition (eg. "SrTiO3").
        thermo_type : str
            Thermo types to return data for (e.g. "GGA_GGA+U").
            Check `mp_api` docs for information on thermo types.
        kwargs : dict
            Kwargs to pass to `MPRester().materials.thermo.get_phase_diagram_from_chemsys`.

        Returns
        -------
        ThermoDoc

        """
        with self.MPRester(self.API_KEY) as mpr:
            docs = mpr.materials.thermo.search(formula=composition,energy_above_hull=(0,0),thermo_types=thermo_types,**kwargs)
        
        if len(docs) > 1:
            warnings.warn('Search returned more than one entry with E above hull = 0 eV, check manually. Returning the first entry...')
        entry = docs[0]
        return entry


    def get_stable_energy_pfu_from_composition(self,composition,thermo_types=['GGA_GGA+U'],**kwargs):
        """
        Pull from MP database the energy per formula unit (pfu) in eV of the
        entry with E above Convex Hull = 0 eV for a target composition.

        Parameters
        ----------
        composition : str
            Target composition (eg. "SrTiO3").
        thermo_type : str
            Thermo types to return data for (e.g. "GGA_GGA+U").
            Check `mp_api` docs for information on thermo types.
        kwargs : dict
            Kwargs to pass to `MPRester().materials.thermo.get_phase_diagram_from_chemsys`.

        Returns
        -------
        energy_pfu : float
            Energy per formula unit in eV.

        """
        entry = self.get_stable_entry_from_composition(composition=composition,thermo_types=thermo_types,**kwargs)
        nfu = entry.composition.get_reduced_composition_and_factor()[1]
        energy_pfu = entry.energy_per_atom * (entry.composition.num_atoms/nfu)
        return energy_pfu
        

    def get_structure(self,final=True,conventional_unit_cell=False):
        """
        Get a Structure corresponding to a material ID.

        Parameters
        ----------
        material_id : str
            Materials Project material_id (a string, e.g., mp-1234).
        final : bool
            Whether to get the final structure, or the initial
            (pre-relaxation) structure.
        conventional_unit_cell : bool
            Whether to get the standard conventional unit cell

        Returns
        -------
        structure : Structure
            Structure object.
            
        """
        with self.MPRester(self.API_KEY) as mpr:
            structure = mpr.get_structure_by_material_id(self.mp_id,final=final,conventional_unit_cell=conventional_unit_cell)
        return structure

    
    
    
    
    
    
    
