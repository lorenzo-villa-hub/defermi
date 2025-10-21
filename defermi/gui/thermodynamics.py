
import streamlit as st
import uuid

from pymatgen.core.composition import Composition


def thermodynamics():
    """
    GUI elements to set DefectThermodynamics parameters
    """
    if "da" in st.session_state:
        st.markdown("**Thermodynamic Parameters**")
        temperature = st.slider("Temperature (K)", 0, 1500, 1000, 50, key="temp")
        if temperature == 0:
            temperature = 0.1 # prevent division by zero
        
        precursors()
        filter_entries_with_missing_elements()
        quenching()


    
def precursors():
    
    if "da" in st.session_state:
        da = st.session_state.da
        st.markdown("**Precursors**")

        # Initialize entries
        if "precursor_entries" not in st.session_state:
            st.session_state.precursor_entries = []
        
        cols = st.columns([0.1, 0.4, 0.4, 0.1])
        with cols[0]:
            if st.button("➕",key="add_precursor"):
                # Generate a unique ID for this entry
                entry_id = str(uuid.uuid4())
                st.session_state.precursor_entries.append({
                    "id": entry_id,
                    "composition": "",
                    "energy": 0.0
                })

        def remove_precursor_entry(entry_id):
            for idx,entry in enumerate(st.session_state.precursor_entries):
                if entry['id'] == entry_id:
                    del st.session_state.precursor_entries[idx]


        for entry in st.session_state.precursor_entries:
            with cols[1]:
                entry["composition"] = st.text_input("Composition", value=entry["composition"], key=f"comp_{entry['id']}")
            with cols[2]:
                entry["energy"] = st.number_input("Energy p.f.u (eV)", value=entry["energy"], step=1.0, key=f"energy_{entry['id']}")
            with cols[3]:
                st.button("🗑️", on_click=remove_precursor_entry, args=[entry['id']], key=f"del_{entry['id']}")

        st.session_state.precursors = {
                            entry["composition"]: entry["energy"] 
                            for entry in st.session_state.precursor_entries
                            if entry["composition"]}



def filter_entries_with_missing_elements():
    """
    Remove defect entries with elements missing from precursors from brouwer diagram dataset.
    """
    if "precursors" in st.session_state and "da" in st.session_state:
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
            quench_temperature = st.slider("Quench Temperature (K)", 0, 1500, 300, 50, key="qt")
            if quench_temperature == 0:
                quench_temperature = 0.1 
            st.session_state.quench_temperature = quench_temperature

            
            quench_mode = st.radio("Quenching mode",("species","elements"),horizontal=True,key="quench_mode",index=0)

            if "brouwer_da" in st.session_state:
                if quench_mode == "species":
                    species = [name for name in st.session_state.brouwer_da.names]
                    st.multiselect("Select quenched species",species,key="quenched_species",default=species)
                    st.session_state.quench_elements = False
                elif quench_mode == "elements":
                    species = set()
                    for entry in st.session_state.brouwer_da:
                        if entry.defect.type == 'Vacancy':
                            species.add(entry.defect.name)
                        else:
                            species.add(entry.defect.specie)
                    st.multiselect("Select quenched elements",species,key="quenched_species",default=species)
                    st.session_state.quench_elements = True
        else:
            st.session_state.quenched_species = None
            st.session_state.quench_elements = False
            st.session_state.quench_temperature = None


