
import os

import streamlit as st

from defermi.gui.initialize import initialize, filter_entries, save_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable

def main():
    st.set_page_config(layout="wide", page_title="defermi")

    left_col, right_col = st.columns([1.5, 1.8])

    with left_col:
        cols = st.columns(2)
        with cols[0]:
            st.title("`defermi`")
        with cols[1]:
            subcols = st.columns(2)
            with subcols[0]:
                pass
            with subcols[1]:
                if st.button("💾 Save Session"):
                    default_save_path = os.path.join(os.getcwd(), "session_state.defermi")
                    file_path = default_save_path#file_path = st.text_input("Session file path:", value=default_save_path)
                    save_session(file_path)

        initialize()
        filter_entries()
        chempots()
        
        st.write('')
        st.divider()
        st.write('')
        
        if st.session_state.da:
            cols = st.columns([0.05,0.95])
            with cols[0]:
                init_state_variable('enable_thermodynamics',value=False)
                enable_thermodynamics = st.checkbox('Enable Thermodynamics', value=st.session_state['enable_thermodynamics'], 
                                                    key='widget_enable_thermodynamics',label_visibility='collapsed')
                st.session_state['enable_thermodynamics'] = enable_thermodynamics
            with cols[1]:
                st.markdown('#### Thermodynamics')
            
            if enable_thermodynamics:
                dos()
                thermodynamics()
        
    with right_col:
        plotter()

if __name__ == "__main__":
    main()