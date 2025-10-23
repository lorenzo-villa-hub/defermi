
import os
import tempfile
import streamlit as st
from monty.json import MontyDecoder

def dos():
    """
    Import DOS file or set effective mass
    """
    if st.session_state.da:
        st.markdown("**Density of states**")

        cols = st.columns([0.5, 0.5])
        with cols[0]:
            dos_type = st.radio("Select",("$m^*/m_e$","DOS"),horizontal=True,key="dos_type",index=0,label_visibility='collapsed')
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
            elif dos_type == '$m^*/m_e$':
                cols = st.columns(2)
                with cols[0]:
                    m_eff_e = st.number_input(f"e", value=1.0, max_value=1.1,step=0.1)
                with cols[1]:
                    m_eff_h = st.number_input(f"h", value=1.0, max_value=1.1,step=0.1)
                dos = {'m_eff_e':m_eff_e, 'm_eff_h':m_eff_h}

        st.session_state.dos = dos
        st.divider()
