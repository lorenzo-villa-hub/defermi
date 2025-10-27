
import os
import tempfile
import streamlit as st
from monty.json import MontyDecoder

from defermi.gui.utils import init_state_variable

def dos():
    """
    Import DOS file or set effective mass
    """
    if st.session_state.da:
        st.markdown("**Density of states**")

        init_state_variable('dos',value=None)

        cols = st.columns([0.5, 0.5])
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
                uploaded_dos = st.file_uploader("Upload", type=["json"], label_visibility="collapsed")
                if uploaded_dos is not None:
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                        tmp.write(uploaded_dos.getbuffer())
                        tmp_path = tmp.name
                        with open(tmp_path) as file:
                            dos = MontyDecoder().decode(file.read())
                    os.unlink(tmp_path)
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
