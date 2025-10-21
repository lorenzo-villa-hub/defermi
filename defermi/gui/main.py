
import streamlit as st

from defermi.gui.initialize import initialize, filter_entries
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics

def main():
    st.set_page_config(layout="wide", page_title="defermi")
    st.title("`defermi`")

    left_col, right_col = st.columns([1.5, 1.8])

    with left_col:

        initialize()
        filter_entries()
        chempots()
        dos()
        thermodynamics()
        
    with right_col:
        pass

if __name__ == "__main__":
    main()