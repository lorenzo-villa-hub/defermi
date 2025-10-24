
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
       # filter_entries_with_missing_elements()
       # quenching()
      #  external_defects()
      #  dopants()


    
def precursors():
    
    if st.session_state.da:
        da = st.session_state.da
        st.markdown("**Precursors**")

        init_state_variable('precursor_entries',value=[])
        
        cols = st.columns([0.1, 0.4, 0.4, 0.1])
        with cols[0]:
            if st.button("➕",key="widget_add_precursor"):
                # Generate a unique ID for this entry
                entry_id = str(uuid.uuid4())
                st.session_state.precursor_entries.append({
                    "id": entry_id,
                    "composition": "",
                    "energy": 0.0
                })

        def remove_precursor_entry(entry_id):
            updated_entries = []
            for idx,entry in enumerate(st.session_state['precursor_entries']):
                if entry['id'] != entry_id:
                    updated_entries.append(st.session_state['precursor_entries'][idx])
            st.session_state['precursor_entries'] = updated_entries.copy()

        def update_composition(entry_id):
            for entry in st.session_state['precursor_entries']:
                if entry['id'] == entry_id:
                    entry['composition'] = st.session_state[f'widget_comp_{entry_id}']

        updated_entries = []
        for entry in st.session_state['precursor_entries']:
            st.write(entry)
            with cols[1]:
                comp = st.text_input("Composition", value=entry["composition"], key=f"widget_comp_{entry['id']}", on_change=update_composition, args=[entry['id']])
            with cols[2]:
                energy = st.number_input("Energy p.f.u (eV)", value=entry["energy"], step=1.0, key=f"widget_energy_{entry['id']}")
            with cols[3]:
                st.button("🗑️", on_click=remove_precursor_entry, args=[entry['id']], key=f"widget_del_{entry['id']}")
            updated_entries.append({"id": entry["id"], "composition": comp, "energy": energy})

        st.session_state.precursor_entries = updated_entries
        st.write(st.session_state['precursor_entries'])
        st.write(updated_entries)
        st.session_state.precursors = {
                            entry["composition"]: entry["energy"] 
                            for entry in st.session_state.precursor_entries
                            if entry["composition"]}

       # st.write(st.session_state['precursor_entries'])


def filter_entries_with_missing_elements():
    """
    Remove defect entries with elements missing from precursors from brouwer diagram dataset.
    """
    if "precursors" in st.session_state and st.session_state.da:
        precursors = st.session_state.precursors
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
            brouwer_da = da.filter_entries(elements=filter_elements)
        else:
            brouwer_da = da        
        st.session_state.brouwer_da = brouwer_da



def quenching():
    """
    GUI elements to set defect quenching parameters.
    """
    if "brouwer_da" in st.session_state: 
        enable_quench = st.checkbox("Enable quenching", value=False, key="enable_quench")
        if enable_quench:
            cols = st.columns(2)
            with cols[0]:
                quench_temperature = st.slider("Quench Temperature (K)", 0, 1500, 300, 50, key="qt")
            if quench_temperature == 0:
                quench_temperature = 0.1 

            with cols[1]:
                quench_mode = st.radio("Quenching mode",("species","elements"),horizontal=True,key="quench_mode",index=0)
            if quench_mode == "species":
                species = [name for name in st.session_state.brouwer_da.names]
                quenched_species = st.multiselect("Select quenched species",species,default=species)
                quench_elements = False
            elif quench_mode == "elements":
                species = set()
                for entry in st.session_state.brouwer_da:
                    if entry.defect.type == 'Vacancy':
                        species.add(entry.defect.name)
                    else:
                        species.add(entry.defect.specie)
                quenched_species = st.multiselect("Select quenched elements",species,default=species)
                quench_elements = True
        
            st.session_state.quench_temperature = quench_temperature
            st.session_state.quenched_species = quenched_species
            st.session_state.quench_elements = quench_elements
        else:
            st.session_state.quench_temperature = None
            st.session_state.quenched_species = None
            st.session_state.quench_elements = None
            
    if "quench_temperature" not in st.session_state:
        st.session_state.quench_temperature = None
    if "quenched_species" not in st.session_state:
        st.session_state.quenched_species = None
    if "quench_elements" not in st.session_state:
        st.session_state.quench_elements = None


def external_defects():
    """
    GUI elements to set external defects.
    """
    if st.session_state.da:
        st.markdown("**External defects**")

        if "external_defects_entries" not in st.session_state:
            st.session_state.external_defects_entries = []

        cols = st.columns([0.11, 0.26, 0.26, 0.26, 0.11])
        with cols[0]:
            if st.button("➕",key="add_external_defect"):
                # Generate a unique ID for this entry
                entry_id = str(uuid.uuid4())
                st.session_state.external_defects_entries.append({
                    "id": entry_id,
                    "name": "",
                    "charge": 0.0,
                    "conc":0.0})

        def remove_external_defects_entries(entry_id):
            for idx,entry in enumerate(st.session_state.external_defects_entries):
                if entry['id'] == entry_id:
                    del st.session_state.external_defects_entries[idx]

        for defect in st.session_state.external_defects_entries:
            with cols[1]:
                defect["name"] = st.text_input("Name", key=f"name_{defect['id']}")
            with cols[2]:
                defect["charge"] = st.number_input("Charge", step=1.0,key=f"charge_{defect['id']}")
            with cols[3]:
                defect["conc"] = st.number_input(r"log₁₀(concentration (cm⁻³))", step=1.0, key=f"conc_{defect['id']}")
                defect["conc"] = 10**defect["conc"]
            with cols[4]:
                st.button("🗑️", on_click=remove_external_defects_entries, args=[defect['id']], key=f"del_{defect['id']}")

        st.session_state.external_defects = [{
                            'name':e['name'],
                            'charge':e['charge'],
                            'conc':e['conc']
                            } for e in st.session_state.external_defects_entries if e["name"]]
        

def dopants():
    if st.session_state.da:
        st.divider()
        st.markdown("**Dopant settings**")

        da = st.session_state.da
        possible_dopants = ["None","Donor","Acceptor"]
        for entry in da:
            if entry.defect.type == "Substitution":
                el = entry.defect.specie
                if el not in possible_dopants:
                    possible_dopants.append(el)
        possible_dopants.append('custom')
        dopant = st.radio("Select dopant",options=possible_dopants,index=0, horizontal=True)
        
        if dopant == "None":
            dopant = None
            conc_range = None
        elif dopant == "Donor":
            cols = st.columns(2)
            with cols[0]:
                charge = st.number_input("Charge", min_value=0.0, value=1.0, step = 1.0, key="charge_dopant")
            with cols[1]:
                min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="widget_conc_range")
            conc_range = ( float(10**min_conc), float(10**max_conc) )
            dopant = {"name":"D","charge":charge}

        elif dopant == "Acceptor":
            cols = st.columns(2)
            with cols[0]:
                charge = st.number_input("Charge", max_value=0.0, value=-1.0, step = 1.0, key="charge_dopant")
            with cols[1]:
                min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="widget_conc_range")
            conc_range = ( float(10**min_conc), float(10**max_conc) )
            dopant = {"name":"A","charge":charge}

        elif dopant == "custom":
            cols = st.columns(3)
            with cols[0]:
                name = st.text_input("Name", key="name_dopant")
            with cols[1]:
                charge = st.number_input("Charge", step=1.0,key="charge_dopant")
            with cols[2]:
                min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="widget_conc_range")
            conc_range = ( float(10**min_conc), float(10**max_conc) )
            dopant = {"name":name,"charge":charge}

        else:
            min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="widget_conc_range")
            conc_range = ( float(10**min_conc), float(10**max_conc) )   

        st.session_state.dopant = dopant
        st.session_state.conc_range = conc_range         

