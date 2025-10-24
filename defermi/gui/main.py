
import os

import streamlit as st

from defermi.gui.initialize import initialize, filter_entries, save_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
from defermi.gui.plotter import plotter

def main():
    st.set_page_config(layout="wide", page_title="defermi")

    left_col, right_col = st.columns([1.5, 1.8])

    with left_col:
        cols = st.columns(2)
        with cols[0]:
            st.title("`dεfermi`")
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
    #    chempots()
        
        st.write('')
        st.divider()
        st.write('')
        
    #    dos()

    #    thermodynamics()
        
    with right_col:
        plotter()

if __name__ == "__main__":
    main()