import tempfile
import os
import time
import json
import io

import matplotlib
import streamlit as st
import pandas as pd



from defermi import DefectsAnalysis 
from defermi.gui.info import file_loader_info, band_gap_info
from defermi.gui.utils import load_session, init_state_variable, widget_with_updating_state


def reset_session():
    st.session_state.clear()
    return


def load_dataframe(uploaded_file):
    name = uploaded_file.name
    if name.endswith('.csv'):
        dataframe = pd.read_csv(uploaded_file) # Streamlit's UploadedFile can be read directly for csv
    elif name.endswith('.pkl'):
        dataframe = pd.read_pickle(io.BytesIO(uploaded_file.getvalue())) # pass the bytes for pickles
    else:
        st.error('Dataset format must be "csv" or "pkl"')
        return None
    return dataframe


def load_file(uploaded_file):
    init_state_variable('session_loaded',value=False)
    if uploaded_file:
        if ".defermi" in uploaded_file.name and not st.session_state['session_loaded']:
            load_session(uploaded_file) 
            st.session_state['session_loaded'] = True
            st.session_state['df_complete'] = st.session_state['saved_dataframe']
        elif '.defermi' not in uploaded_file.name and not st.session_state['session_loaded']:
            st.session_state['input_dataframe'] = load_dataframe(uploaded_file)


def band_gap_vbm_inputs():
    init_state_variable('band_gap',value=None)
    init_state_variable('vbm',value=0.0)

    cols = st.columns([0.45,0.45,0.1])
    with cols[0]:
        band_gap = st.number_input("Band gap (eV)", value=st.session_state['band_gap'], step=0.1, placeholder="Enter band gap", key='widget_band_gap')
        if band_gap is None:
            st.warning('Enter band gap to begin session')
        st.session_state['band_gap'] = band_gap
    with cols[1]:
        vbm = st.number_input("VBM (eV)", value=st.session_state['vbm'], step=0.1, key='widget_vbm')
        st.session_state['vbm'] = vbm
    with cols[2]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(band_gap_info)
    return 


def main_inputs():

    init_state_variable('da',value=None)

    st.markdown('## 📂 File')
    cols = st.columns([0.9,0.1])
    with cols[0]:
        uploaded_file = st.file_uploader("upload", type=["defermi","csv","pkl"], on_change=reset_session, label_visibility="collapsed")
        load_file(uploaded_file)
    with cols[1]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(file_loader_info)

    if uploaded_file:
        band_gap_vbm_inputs()
        if st.session_state['band_gap']:
            if not st.session_state['da']:
                df = st.session_state['input_dataframe']
                st.session_state['da'] = DefectsAnalysis.from_dataframe(
                                                                    df,
                                                                    band_gap=st.session_state['band_gap'],
                                                                    vbm=st.session_state['vbm'])
            else:
                st.session_state['da'].band_gap = st.session_state['band_gap']
                st.session_state['da'].vbm = st.session_state['vbm']

            if 'init' not in st.session_state:
                # message disappears after 1 second 
                msg = st.empty()
                msg.success("Dataset initialized")
                time.sleep(1)
                msg.empty()
                st.session_state.init = True
    
        st.divider()



def filter_entries():
    """
    GUI elements to filter defect entries in DefectsAnalysis
    """
    if st.session_state.da:
        st.session_state['da'].band_gap = st.session_state['band_gap']
        st.session_state['da'].vbm = st.session_state['vbm']
        init_state_variable('original_da',value=st.session_state.da.copy())
        
        df_complete = st.session_state.original_da.to_dataframe(include_data=False,include_structures=False) 
        df_complete['Include'] = [True for i in range(len(df_complete))]
        cols = ['Include'] + [col for col in df_complete.columns if col != 'Include']
        df_complete = df_complete[cols]

        init_state_variable('df_complete',value=df_complete)    
        init_state_variable('dataframe',value=df_complete)
        init_state_variable('saved_dataframe',value=df_complete)
        
        st.session_state.da = DefectsAnalysis.from_dataframe(
                                                    st.session_state['dataframe'],
                                                    band_gap=st.session_state['band_gap'],
                                                    vbm=st.session_state['vbm'],
                                                    include_data=False)  

