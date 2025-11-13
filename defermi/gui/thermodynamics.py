
import numpy as np
import uuid
import streamlit as st

from defermi.gui.info import quenching_info, external_defects_info
from defermi.gui.utils import init_state_variable


def thermodynamics():
    if st.session_state.da:
        init_state_variable('temperature',value=1000)
        st.markdown("### Temperature (K)")
        temperature = st.slider("Temperature (K)", min_value=0, max_value=1500, value=st.session_state['temperature'], 
                                step=50, key="widget_temperature",label_visibility='collapsed')
        if temperature == 0:
            temperature = 0.1 # prevent division by zero
        st.session_state['temperature'] = temperature

        quenching()
        external_defects()

        st.divider()


def quenching():
    """
    GUI elements to set defect quenching parameters.
    """
    init_state_variable('enable_quench',value=False)
    init_state_variable('quench_temperature',value=None)
    init_state_variable('quench_mode',value='species')
    init_state_variable('quenched_species',value=None)
    init_state_variable('quench_elements',value=None)

    enable_quench = st.checkbox("Enable quenching", value=st.session_state['enable_quench'], key="widget_enable_quench")
    st.session_state['enable_quench'] = enable_quench
    if enable_quench:
        cols = st.columns([0.45,0.45,0.1])
        with cols[2]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(quenching_info)
        with cols[0]:
            st.session_state['quench_temperature'] = 300
            quench_temperature = st.slider("Quench Temperature (K)", min_value=0, max_value=1500, 
                                        value=st.session_state['quench_temperature'], step=50, key="widget_quench_temperature")
            st.session_state['quench_temperature'] = quench_temperature
        if st.session_state['quench_temperature'] == 0:
            st.session_state['quench_temperature'] = 0.1 

        with cols[1]:
            index = 0 if st.session_state['quench_mode'] == 'species' else 1
            quench_mode = st.radio("Quenching mode",("species","elements"),horizontal=True,key="widget_quench_mode",index=index)

        if quench_mode == "species":
            species = set()
            for entry in st.session_state.da:
                for df in entry.defect:
                    species.add(df.name)
            default = st.session_state['quenched_species'] or species
            if st.session_state['quenched_species']:
                for name in st.session_state['quenched_species']:
                    if name not in species:
                        default = species
            quenched_species = st.multiselect("Select quenched species",options=species,default=default,key='widget_quenched_species')
            quench_elements = False

        elif quench_mode == "elements":
            species = set()
            for entry in st.session_state['da']:
                if entry.defect.type == 'Vacancy':
                    species.add(entry.defect.name)
                else:
                    for df in entry.defect:
                        species.add(df.specie)
            if st.session_state['quench_elements']:
                default = st.session_state['quenched_species'] or species
            else:
                default = species
            quenched_species = st.multiselect("Select quenched elements",options=species,default=default,key='widget_quenched_elements')
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
    cols = st.columns([0.9,0.1])
    with cols[0]:
        st.markdown("**External defects**")
    with cols[1]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(external_defects_info)

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
            conc = st.number_input(r"log₁₀(c (cm⁻³))", value=value, step=1, key=f"widget_conc_{defect['id']}")
            defect["conc"] = 10**conc 
        with cols[4]:
            st.button("🗑️", on_click=remove_external_defects_entries, args=[defect['id']], key=f"widget_del_{defect['id']}")

    st.session_state['external_defects'] = [{
                        'name':e['name'],
                        'charge':e['charge'],
                        'conc':e['conc']
                        } for e in st.session_state.external_defects_entries if e["name"]]
        