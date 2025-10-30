
import os
import io
import matplotlib

import streamlit as st

from defermi import DefectsAnalysis

from defermi.gui.initialize import initialize, filter_entries, load_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable
import defermi.gui

def main():
    st.set_page_config(layout="wide", page_title="defermi")

    left_col, right_col = st.columns([1.5, 1.8])

    with left_col:
        cols = st.columns(2)
        with cols[0]:
            st.title("`defermi`")
  
        init_state_variable('session_loaded',value=False)
        if not st.session_state['session_loaded']:
            session_file = os.path.join(defermi.gui.__path__[0],'app_example.defermi')
            load_session(session_file)
            st.session_state['session_loaded'] = True

        initialize(defects_analysis=st.session_state['da'])
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