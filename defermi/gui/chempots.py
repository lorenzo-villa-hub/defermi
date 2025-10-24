
import streamlit as st

from defermi.gui.utils import init_state_variable

def chempots():
    """
    GUI elements for chemical potentials 
    """
    if st.session_state.da:
        da = st.session_state.da

        st.markdown("**Chemical Potentials (eV)**")
        mu_string = "μ"

        init_state_variable('chempots',value={})

        cols = st.columns(5)
        for idx,el in enumerate(da.elements):
            ncolumns = 5
            col_idx = idx%ncolumns
            with cols[col_idx]:
                value = st.session_state['chempots'][el] if el in st.session_state['chempots'] else 0.0
                st.session_state.chempots[el] = st.number_input(f"{mu_string}({el})", value=value, max_value=0.0,step=0.5, key=f'widget_chempot{el}')