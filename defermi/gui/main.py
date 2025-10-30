
import os
import io

import streamlit as st

from defermi.gui.initialize import initialize, filter_entries, save_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable

def main():
    st.set_page_config(layout="wide", page_title="defermi")

    left_col, space1, middle_line, space2, right_col = st.columns([1.5, 0.05, 0.05,0.05, 1.7])

    with left_col:
        cols = st.columns(2)
        with cols[0]:
            st.title("`defermi`")
        with cols[1]:
            subcols = st.columns(2)
            with subcols[0]:
                pass
            with subcols[1]:
                init_state_variable('session_name',value='session')
                filename = st.session_state['session_name'] + '.defermi'
                save_session(filename)

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
    
    with middle_line:
        pass
        #st.markdown("<div style='border-left: 1px solid #999; height: 2000px; margin: auto;'></div>",unsafe_allow_html=True)

    with right_col:
        plotter()

if __name__ == "__main__":
    main()