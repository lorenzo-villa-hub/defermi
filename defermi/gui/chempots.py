
import streamlit as st

def chempots():
    """
    GUI elements for chemical potentials 
    """
    if st.session_state.da:
        da = st.session_state.da

        st.markdown("**Chemical Potentials (eV)**")
        mu_string = "μ"

        if "chempots" not in st.session_state:    
            st.session_state.chempots = {}

        cols = st.columns(5)
        for idx,el in enumerate(da.elements):
            ncolumns = 5
            col_idx = idx%ncolumns
            with cols[col_idx]:
                st.session_state.chempots[el] = st.number_input(f"{mu_string}({el})", value=0.0, max_value=0.0,step=0.5)