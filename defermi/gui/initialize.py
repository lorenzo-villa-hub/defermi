
import streamlit as st

from defermi import DefectsAnalysis
from defermi.gui.defaults import get_default_df
from defermi.gui.utils import init_state_variable


def initialize_state_variables():
    init_state_variable('session_loaded',value=False)
    init_state_variable('session_name',value='session')
    init_state_variable('band_gap',value=None)


def initialize_defects_analysis(df_complete):
    st.session_state.da = None
    df_complete = df_complete.dropna()
    if df_complete.empty:
        st.warning('Dataset is empty')
    elif st.session_state['band_gap'] and 'vbm' in st.session_state:
        df_to_import = df_complete[df_complete["Include"] == True] # keep only selected rows
        st.session_state.da = DefectsAnalysis.from_dataframe(
                                                    df_to_import,
                                                    band_gap=st.session_state['band_gap'],
                                                    vbm=st.session_state['vbm'],
                                                    include_data=False) 
    return


def initialize_complete_dataframe():
    key = 'complete_dataframe'
    input_key = 'input_dataframe'  
    if input_key in st.session_state:
        if key not in st.session_state or st.session_state[key].empty:
            st.session_state[key] = st.session_state[input_key]
    else:
        if key not in st.session_state:
            st.session_state[key] = get_default_df()
    return
