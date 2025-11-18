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


def upload_file():
    st.markdown('## 📂 File')
    cols = st.columns([0.9,0.1])
    with cols[0]:
        uploaded_file = st.file_uploader("upload", type=["defermi","csv","pkl"], on_change=reset_session, label_visibility="collapsed")
        load_file(uploaded_file)
    with cols[1]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(file_loader_info)
    return


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
        elif '.defermi' not in uploaded_file.name and not st.session_state['session_loaded']:
            df = load_dataframe(uploaded_file)            
            df['Include'] = [True for i in range(len(df))]
            cols = ['Include'] + [col for col in df.columns if col != 'Include']
            df = df[cols]
            st.session_state['input_dataframe'] = df
            st.session_state['session_name'] = uploaded_file.name.split('.')[0]
    return


def band_gap_vbm_inputs():
    init_state_variable('band_gap',value=None)
    init_state_variable('vbm',value=0.0)
    cols = st.columns([0.45,0.45,0.1])
    with cols[0]:
        band_gap = st.number_input("Band gap (eV)", value=st.session_state['band_gap'], step=0.1, placeholder="Enter band gap", key='widget_band_gap')
        st.session_state['band_gap'] = band_gap
        if st.session_state['band_gap'] is None:
            st.warning('Enter band gap to begin session')
        
    with cols[1]:
        vbm = st.number_input("VBM (eV)", value=st.session_state['vbm'], step=0.1, key='widget_vbm')
        st.session_state['vbm'] = vbm
    with cols[2]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(band_gap_info)
    return 



