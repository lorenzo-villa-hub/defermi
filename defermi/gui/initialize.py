
import tempfile
import os
import time
import json

import matplotlib
import streamlit as st

from monty.json import jsanitize, MontyEncoder, MontyDecoder

from defermi import DefectsAnalysis 
from defermi.gui.utils import init_state_variable, widget_with_updating_state


def initialize():
    """
    Import dataframe file to initialize DefectsAnalysis object
    """
    if "color_sequence" not in st.session_state:
        st.session_state['color_sequence'] = matplotlib.color_sequences['tab10']

    def reset_da():
        if "da" in st.session_state:
            st.session_state.da = None
        return

    st.markdown('##### 📂 Load Session or Dataset')
    uploaded_file = st.file_uploader("upload", type=["defermi","csv","json","pkl"], on_change=reset_da, label_visibility="collapsed")

    init_state_variable('da',value=None)
    init_state_variable('session_loaded', value=False)
    if uploaded_file is not None:
        _, ext = os.path.splitext(uploaded_file.name)
        if not ext:
            ext = ".tmp"  # fallback if no extension present
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        if ".defermi" in tmp_path and not st.session_state['session_loaded']:
            load_session(tmp_path) 
            st.session_state['session_loaded'] = True

        cols = st.columns(2)
        with cols[0]:
            if "band_gap" not in st.session_state:
                st.session_state['band_gap'] = None
            band_gap = st.number_input("Band gap (eV)", value=st.session_state['band_gap'], step=0.1, placeholder="Enter band gap", key='widget_band_gap')
            st.session_state['band_gap'] = band_gap
        with cols[1]:
            if "vbm" not in st.session_state:
                st.session_state['vbm'] = 0.0
            vbm = st.number_input("VBM (eV)", value=st.session_state['vbm'], step=0.1, key='widget_vbm')
            st.session_state['vbm'] = vbm

        if st.session_state['band_gap']:
            if not st.session_state['da']:
                st.session_state['da'] = DefectsAnalysis.from_file(tmp_path, band_gap=st.session_state.band_gap, vbm=st.session_state.vbm)
            else:
                st.session_state['da'].band_gap = st.session_state['band_gap']
                st.session_state['da'].vbm = st.session_state['vbm']
            
            if not "color_dict" in st.session_state:
                st.session_state.color_dict = {name:st.session_state.color_sequence[idx] for idx,name in enumerate(st.session_state.da.names)}
        #    st.write(st.session_state['color_dict'])
            # clean up the temp file
            os.unlink(tmp_path)
            if 'init' not in st.session_state:
                    # message disappears after 1 second 
                    msg = st.empty()
                    msg.success("Dataset initialized")
                    time.sleep(1)
                    msg.empty()
                    st.session_state.init = True


def filter_entries():
    """
    GUI elements to filter defect entries in DefectsAnalysis
    """
    if st.session_state.da:

        init_state_variable('original_da',value=st.session_state.da.copy())
        st.session_state['original_da'].band_gap = st.session_state['band_gap']
        st.session_state['original_da'].vbm = st.session_state['vbm']
        
        init_state_variable('mode',value='and')
        init_state_variable('exclude',value=False)
        init_state_variable('types',value=None)
        init_state_variable('elements',value=None)
        init_state_variable('names',value=None)


        st.markdown('**Filter entries**')
        cols = st.columns([0.11,0.25,0.22,0.28,0.15])
        with cols[0]:
            index = 0 if st.session_state['mode'] == 'and' else 1
            mode = st.radio("Mode",options=["and","or"], index=index)
            st.session_state['mode'] = mode
        with cols[1]:
            defect_types = []
            for entry in st.session_state['original_da']:
                dtype = entry.defect.type
                if dtype not in defect_types:
                    defect_types.append(dtype)
            types = widget_with_updating_state(function=st.multiselect,key='types',widget_key='widget_types',label='Types',
                                                  options=defect_types,default=st.session_state['types'])

        with cols[2]:
            defect_elements = st.session_state['original_da'].elements
            elements = widget_with_updating_state(function=st.multiselect, key='elements',label='Elements',
                                                     options=defect_elements, default=st.session_state['elements'])
        with cols[3]:
            defect_names = st.session_state['original_da'].names
            names = widget_with_updating_state(function=st.multiselect, key='names',label='Names',
                                                     options=defect_names, default=st.session_state['names'])
        with cols[4]:
            exclude = widget_with_updating_state(function=st.checkbox, key='exclude',label='Exclude',value=st.session_state['exclude'])

        try:
            st.session_state.da = st.session_state.original_da.filter_entries(
                                                                inplace=False,
                                                                mode=mode,
                                                                exclude=exclude,
                                                                types=types,
                                                                elements=elements,
                                                                names=names)
            st.session_state['eform_names'] = st.session_state['da'].names
        except AttributeError:
            st.warning('Dataset is empty')

        df = st.session_state.da.table(display=['energy_diff']).drop('delta atoms',axis=1)
        st.dataframe(df)


def _delete_dict_key(d,key):
    if key in d:
        del d[key]
    return


def save_session(file_path):
    """Save Streamlit session state to a JSON file."""
    try:
        data = {k:v for k,v in st.session_state.items() if 'widget' not in k}
        _delete_dict_key(data,'precursors')
        _delete_dict_key(data,'session_loaded')
        d = MontyEncoder().encode(data)
        folder = os.path.dirname(file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(d, f, indent=2)
        
        msg = st.empty()
        msg.success(f"Session saved to {file_path}")
        time.sleep(2)
        msg.empty()
    except Exception as e:
        st.error(f"Failed to save session: {e}")


def load_session(file_path):
    """Load Streamlit session state from JSON file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                d = json.load(f)
            d = MontyDecoder().decode(d)
            st.session_state.update(d)
        else:
            st.warning(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Failed to load session: {e}")