
import os
import json
import streamlit as st
from monty.json import MontyDecoder

from defermi.gui.info import dos_info
from defermi.gui.utils import init_state_variable

def dos():
    """
    Import DOS file or set effective mass
    """
    if st.session_state.da:
        st.markdown("# Thermodynamic Parameters")
        cols = st.columns([0.9,0.1])
        with cols[0]:
            st.markdown("**Density of states**")
        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(dos_info)

        init_state_variable('dos',value=None)

        cols = st.columns([0.2, 0.8])
        with cols[0]:
            if not st.session_state['dos']:
                index = 0
            elif st.session_state['dos_type'] == "$m^*/m_e$":
                index = 0
            elif st.session_state['dos_type'] == 'DOS':
                index = 1
            dos_type = st.radio("Select",("$m^*/m_e$","DOS"),horizontal=True,index=index,label_visibility='collapsed',key='widget_dos_type')
            st.session_state['dos_type'] = dos_type
        with cols[1]:
            if dos_type == "DOS":
                subcols = st.columns([0.5,0.5])
                with subcols[0]:
                    with st.expander('🗄️ Database'):
                        subsubcols = st.columns([0.7,0.3])
                        with subsubcols[0]:
                            composition = st.text_input(label='Composition',key='widget_dos_composition_DB')
                            if composition:
                                if st.button("Pull",key='widget_pull_dos_DB'):
                                    dos = pull_dos_from_stable_composition(composition=composition)
                                    st.session_state['dos'] = dos
                with subcols[1]:
                    uploaded_dos = st.file_uploader("Upload", type=["json"], label_visibility="collapsed")
                    if uploaded_dos is not None:
                        data_bytes = uploaded_dos.getvalue() # file content as bytes
                        data_str = data_bytes.decode('utf-8') # decode bytes to string (JSON text)
                        json_str = json.loads(data_str)                        
                        dos = MontyDecoder().decode(json_str)
                        st.session_state['dos'] = dos
            elif dos_type == '$m^*/m_e$':
                cols = st.columns(2)
                with cols[0]:
                    if st.session_state['dos'] and type(st.session_state['dos']) == dict and 'm_eff_e' in st.session_state['dos']:
                        value = st.session_state['dos']['m_eff_e']
                    else:
                        st.session_state['dos'] = {}
                        value = 1.0
                    m_eff_e = st.number_input(f"e", value=value, max_value=1.1,step=0.1, key='widget_dos_m_eff_e')
                    st.session_state['dos']['m_eff_e'] = m_eff_e
                with cols[1]:
                    if st.session_state['dos'] and type(st.session_state['dos']) == dict and 'm_eff_h' in st.session_state['dos']:
                        value = st.session_state['dos']['m_eff_h']
                    else:
                        value = 1.0
                    m_eff_h = st.number_input(f"h", value=value, max_value=1.1,step=0.1, key='widget_dos_m_eff_h')
                    st.session_state['dos']['m_eff_h'] = m_eff_h

        st.divider()


def pull_dos_from_stable_composition(composition,thermo_types=['GGA_GGA+U'],**kwargs):
    import base64
    from defermi.tools.materials_project import MPDatabase

    API_KEY = base64.b64decode('Q0FVMk8yODZmRUI2cGJWOUszTU9qblFFUFJkZW9BQXg=').decode()
    dos = MPDatabase(API_KEY=API_KEY).get_dos_from_stable_composition(
                                                                        composition=composition,
                                                                        thermo_types=thermo_types,
                                                                        **kwargs)
    return dos
