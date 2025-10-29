
import numpy as np

import streamlit as st
import uuid

from pymatgen.core.composition import Composition

from defermi.gui.utils import init_state_variable

def thermodynamics():
    """
    GUI elements to set DefectThermodynamics parameters
    """
    if st.session_state.da:
        st.markdown("**Thermodynamic Parameters**")
        init_state_variable('temperature',value=1000)
        init_state_variable('oxygen_ref',value=-4.95)

        cols = st.columns(2)
        with cols[0]:
            temperature = st.slider("Temperature (K)", min_value=0, max_value=1500, value=st.session_state['temperature'], step=50, key="widget_temperature")
            if temperature == 0:
                temperature = 0.1 # prevent division by zero
            st.session_state['temperature'] = temperature
        with cols[1]:
            oxygen_ref = st.number_input("μO (0K, p0) [eV]", value=st.session_state['oxygen_ref'], step=0.5, key='widget_oxygen_ref')
            st.session_state['oxygen_ref'] = oxygen_ref
        
        precursors()
        filter_entries_with_missing_elements()
        quenching()
        external_defects()
        dopants()


    
def precursors():
    
    if st.session_state.da:
        da = st.session_state.da
        st.markdown("**Precursors**")

        init_state_variable('precursor_entries',value=[]) 
        
        cols = st.columns([0.1, 0.4, 0.4, 0.1])
        with cols[0]:
            add_precursors = st.button("➕",key="widget_add_precursor")
            if add_precursors:
                # Generate a unique ID for this entry
                entry_id = str(uuid.uuid4())
                st.session_state.precursor_entries.append({
                    "id": entry_id,
                    "composition": "",
                    "energy": 0.0
                })

        def remove_precursor_entry(entry_id):
            for idx,entry in enumerate(st.session_state['precursor_entries']):
                if entry['id'] == entry_id:
                    del st.session_state['precursor_entries'][idx]


        for entry in st.session_state['precursor_entries']:
            with cols[1]:
                entry["composition"] = st.text_input("Composition", value=entry["composition"], key=f"widget_comp_{entry['id']}")
            with cols[2]:
                entry["energy"] = st.number_input("Energy p.f.u (eV)", value=entry["energy"], step=1.0, key=f"widget_energy_{entry['id']}")
            with cols[3]:
                st.button("🗑️", on_click=remove_precursor_entry, args=[entry['id']], key=f"widget_del_{entry['id']}")

        st.session_state['precursors'] = {
                            entry["composition"]: entry["energy"] 
                            for entry in st.session_state.precursor_entries
                            if entry["composition"]}



def filter_entries_with_missing_elements():
    """
    Remove defect entries with elements missing from precursors from brouwer diagram dataset.
    """
    if "precursors" in st.session_state and st.session_state.da:
        precursors = st.session_state['precursors']
        da = st.session_state.da
        # remove defect entries with missing precursors from brouwer diagram dataset
        elements_in_precursors = set()
        if precursors:
            for comp in precursors:
                if comp:
                    for element in Composition(comp).elements:
                        elements_in_precursors.add(element.symbol)

        filter_elements = set()
        missing_elements = set()
        for el in da.elements:
            if el in elements_in_precursors:
                filter_elements.add(el)
            else:
                missing_elements.add(el)

        cols = st.columns(5)
        for idx,el in enumerate(missing_elements):
            ncolumns = 5
            col_idx = idx%ncolumns
            with cols[col_idx]:
                st.warning(f'{el} missing from precursors')

        if filter_elements:
            try:
                brouwer_da = da.filter_entries(elements=filter_elements)
            except AttributeError:
                st.warning('No entries for Brouwer diagram calculation')
                brouwer_da = None
        else:
            brouwer_da = None       
        st.session_state['brouwer_da'] = brouwer_da



def quenching():
    """
    GUI elements to set defect quenching parameters.
    """
    init_state_variable('enable_quench',value=False)
    init_state_variable('quench_temperature',value=None)
    init_state_variable('quench_mode',value='species')
    init_state_variable('quenched_species',value=None)
    init_state_variable('quench_elements',value=None)

    if "brouwer_da" in st.session_state:
        if st.session_state['brouwer_da']:
            enable_quench = st.checkbox("Enable quenching", value=st.session_state['enable_quench'], key="widget_enable_quench")
            st.session_state['enable_quench'] = enable_quench
            if enable_quench:
                cols = st.columns(2)
                with cols[0]:
                    st.session_state['quench_temperature'] = 300
                    quench_temperature = st.slider("Quench Temperature (K)", min_value=0, max_value=1500, 
                                                value=st.session_state['quench_temperature'], step=50, key="widget_quench_temperature")
                if st.session_state['quench_temperature'] == 0:
                    st.session_state['quench_temperature'] = 0.1 

                with cols[1]:
                    index = 0 if st.session_state['quench_mode'] == 'species' else 1
                    quench_mode = st.radio("Quenching mode",("species","elements"),horizontal=True,key="widget_quench_mode",index=index)
                if quench_mode == "species":
                    species = [name for name in st.session_state.brouwer_da.names]
                    value = st.session_state['quenched_species'] or species
                    quenched_species = st.multiselect("Select quenched species",species,default=value,key='widget_quenched_species')
                    quench_elements = False
                elif quench_mode == "elements":
                    species = set()
                    for entry in st.session_state['brouwer_da']:
                        if entry.defect.type == 'Vacancy':
                            species.add(entry.defect.name)
                        else:
                            species.add(entry.defect.specie)
                    value = st.session_state['quenched_species'] or species
                    quenched_species = st.multiselect("Select quenched elements",species,default=value,key='widget_quenched_elements')
                    quench_elements = True
            
                st.session_state['quenched_species'] = quenched_species
                st.session_state['quench_elements'] = quench_elements
            else:
                st.session_state['quenched_species'] = None
                st.session_state['quench_elements'] = False
                st.session_state['quench_temperature'] = None


def external_defects():
    """
    GUI elements to set external defects.
    """
    if st.session_state.da:
        st.markdown("**External defects**")

        init_state_variable('external_defects_entries',value=[])

        cols = st.columns([0.11, 0.26, 0.26, 0.26, 0.11])
        with cols[0]:
            if st.button("➕",key="widget_add_external_defect"):
                # Generate a unique ID for this entry
                entry_id = str(uuid.uuid4())
                st.session_state['external_defects_entries'].append({
                    "id": entry_id,
                    "name": "",
                    "charge": 0.0,
                    "conc":1.0})

        def remove_external_defects_entries(entry_id):
            for idx,entry in enumerate(st.session_state['external_defects_entries']):
                if entry['id'] == entry_id:
                    del st.session_state['external_defects_entries'][idx]

        for defect in st.session_state['external_defects_entries']:
            with cols[1]:
                name = st.text_input("Name",value=defect['name'], key=f"widget_name_{defect['id']}")
                defect["name"] = name
            with cols[2]:
                charge = st.number_input("Charge", value=defect['charge'], step=1.0,key=f"widget_charge_{defect['id']}")
                defect["charge"] = charge
            with cols[3]:
                value = int(np.log10(float(defect['conc']))) if defect['conc'] else 0
                conc = st.number_input(r"log₁₀(concentration (cm⁻³))", value=value, step=1, key=f"widget_conc_{defect['id']}")
                defect["conc"] = 10**conc 
            with cols[4]:
                st.button("🗑️", on_click=remove_external_defects_entries, args=[defect['id']], key=f"widget_del_{defect['id']}")

        st.session_state['external_defects'] = [{
                            'name':e['name'],
                            'charge':e['charge'],
                            'conc':e['conc']
                            } for e in st.session_state.external_defects_entries if e["name"]]
        

def dopants():
    if st.session_state.da:
        st.divider()
        st.markdown("**Dopant settings**")
        init_state_variable('dopant_type',value='None')
        init_state_variable('conc_range',value=None)
        init_state_variable('dopant',value={})

        da = st.session_state.da
        possible_dopants = ["None","Donor","Acceptor"]
        for entry in da:
            if entry.defect.type == "Substitution":
                el = entry.defect.specie
                if el not in possible_dopants:
                    possible_dopants.append(el)
        possible_dopants.append('custom')

        def update_dopant_type_index():
            st.session_state['dopant_type'] = st.session_state['widget_select_dopant']
        
        if st.session_state['dopant_type'] in possible_dopants:
            st.session_state['dopant_type_index'] = possible_dopants.index(st.session_state['dopant_type'])
        else:
            st.session_state['dopant_type_index'] = 0
        st.radio("Select dopant",options=possible_dopants,index=st.session_state['dopant_type_index'],
                                        horizontal=True, key='widget_select_dopant',on_change=update_dopant_type_index)

        dopant_type = st.session_state['dopant_type']    
        if dopant_type == "None":
            st.session_state['dopant'] = None
            st.session_state['conc_range'] = None
        elif dopant_type == "Donor":
            cols = st.columns(2)
            with cols[0]:
                d = st.session_state['dopant']
                if d and type(d) == dict and 'charge' in d and d['charge'] > 0: 
                    value = d['charge']
                else:
                    value = 1.0 
                charge = st.number_input("Charge", min_value=0.0, value=value, step = 1.0, key="widget_donor_charge")
            with cols[1]:

                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )
                
                if st.session_state['conc_range']:
                    value = int(np.log10(float(st.session_state['conc_range'] [0]))), int(np.log10(float(st.session_state['conc_range'] [1])))
                else:
                    value = (5,18)        
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                                    key="widget_conc_range",on_change=update_conc_range)
            
            st.session_state['dopant'] = {"name":"D","charge":charge}

        elif dopant_type == "Acceptor":
            cols = st.columns(2)
            with cols[0]:
                d = st.session_state['dopant']
                if d and type(d) == dict and 'charge' in d and d['charge'] < 0: 
                    value = d['charge']
                else:
                    value = -1.0 
                charge = st.number_input("Charge", max_value=0.0, value=value, step = 1.0, key="widget_acceptor_charge")
            with cols[1]:
                
                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )

                if st.session_state['conc_range']:
                    value = int(np.log10(float(st.session_state['conc_range'] [0]))), int(np.log10(float(st.session_state['conc_range'] [1])))
                else:
                    value = (5,18)         
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                                    key="widget_conc_range",on_change=update_conc_range)
            
            st.session_state['dopant'] = {"name":"A","charge":charge}

        elif dopant_type == "custom":

            cols = st.columns(3)
            d = st.session_state['dopant']
            with cols[0]:
                value = d['name'] if 'name' in d else ''
                name = st.text_input("Name",value=value, key="widget_name_dopant")          
            with cols[1]:
                if d and type(d) == dict and 'charge' in d:
                    value = d['charge']
                else:
                    value = 0.0
                charge = st.number_input("Charge", value=value, step = 1.0, key="widget_dopant_charge")
            with cols[2]:  
                              
                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )

                if st.session_state['conc_range']:
                    value = int(np.log10(float(st.session_state['conc_range'] [0]))), int(np.log10(float(st.session_state['conc_range'] [1])))
                else:
                    value = (5,18)         
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                                    key="widget_conc_range",on_change=update_conc_range)

                st.session_state['dopant'] = {"name":name,"charge":charge}

        else:
            cols = st.columns(3)
            with cols[2]:
                st.session_state['dopant'] = dopant_type

                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )

                if st.session_state['conc_range']:
                    value = int(np.log10(st.session_state['conc_range'] [0])), int(np.log10(st.session_state['conc_range'] [1]))
                else:
                    value = (5,18)      
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                        key="widget_conc_range",on_change=update_conc_range)
            
    
    if st.session_state['dopant']:
        if not st.session_state['conc_range']:
            st.session_state['conc_range'] = (1e05,1e18)


