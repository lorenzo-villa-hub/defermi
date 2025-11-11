import tempfile
import os
import time
import json

import matplotlib
import streamlit as st
import pandas as pd

from monty.json import jsanitize, MontyEncoder, MontyDecoder

from defermi import DefectsAnalysis 
from defermi.gui.utils import init_state_variable, widget_with_updating_state


def initialize(defects_analysis=None):
    """
    Import dataframe file to initialize DefectsAnalysis object
    """
    if "color_sequence" not in st.session_state:
        st.session_state['color_sequence'] = matplotlib.color_sequences['tab10']
        st.session_state['color_sequence'] += matplotlib.color_sequences['tab20']
        st.session_state['color_sequence'] += matplotlib.color_sequences['Pastel1']

    def reset_session():
        st.session_state.clear()
        return

    if defects_analysis:
        init_state_variable('da',value=defects_analysis)
        uploaded_file = None
    else:
        cols = st.columns([0.7,0.3])
        with cols[0]:
            st.markdown('## 📂 File')
            init_state_variable('da',value=None)
            uploaded_file = st.file_uploader("upload", type=["defermi","csv","json","pkl"], on_change=reset_session, label_visibility="collapsed")
        with cols[1]:
            subcols = st.columns([0.8,0.2])
            init_state_variable('session_name',value='session')
            filename = st.session_state['session_name'] + '.defermi'
            with subcols[0]:
                st.markdown("<br><br>", unsafe_allow_html=True)
                save_session(filename)
            with subcols[1]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(file_loader_info)


    init_state_variable('session_loaded', value=False)
    init_state_variable('session_name',value='')

    if uploaded_file is not None:
        st.session_state['session_name'] = uploaded_file.name.split('.')[0] # use file name to name session
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
            st.session_state['df_complete'] = st.session_state['saved_dataframe']

        cols = st.columns([0.45,0.45,0.1])
        with cols[0]:
            if "band_gap" not in st.session_state:
                st.session_state['band_gap'] = None
            band_gap = st.number_input("Band gap (eV)", value=st.session_state['band_gap'], step=0.1, placeholder="Enter band gap", key='widget_band_gap')
            if band_gap is None:
                st.warning('Enter band gap to begin session')
            st.session_state['band_gap'] = band_gap
        with cols[1]:
            if "vbm" not in st.session_state:
                st.session_state['vbm'] = 0.0
            vbm = st.number_input("VBM (eV)", value=st.session_state['vbm'], step=0.1, key='widget_vbm')
            st.session_state['vbm'] = vbm
        with cols[2]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(band_gap_info)

        if st.session_state['band_gap']:
            if not st.session_state['da']:
                st.session_state['da'] = DefectsAnalysis.from_file(tmp_path, band_gap=st.session_state.band_gap, vbm=st.session_state.vbm)
            else:
                st.session_state['da'].band_gap = st.session_state['band_gap']
                st.session_state['da'].vbm = st.session_state['vbm']
            
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



def _delete_dict_key(d,key):
    if key in d:
        del d[key]
    return


def save_session(filename):
    """Save Streamlit session state to a JSON file."""
    try:
        data = {k:v for k,v in st.session_state.items() if 'widget' not in k}

        _delete_dict_key(data,'session_loaded')
        _delete_dict_key(data,'session_name')
        _delete_dict_key(data,'precursors')
        _delete_dict_key(data,'external_defects')
        _delete_dict_key(data,'edit_dataframe')
        _delete_dict_key(data,'df_complete')
        _delete_dict_key(data,'formation_energies_figure')

        d = MontyEncoder().encode(data)

        # convert to pretty JSON string
        json_str = json.dumps(d, indent=2)

        # create a downloadable button
        st.download_button(
            label="💾 Save Session",
            data=json_str,
            file_name=filename,
            mime="application/json"
        )

    except Exception as e:
        st.error(f"Failed to prepare session download: {e}")


def load_session(file_path):
    """Load Streamlit session state from JSON file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                json_string = json.load(f)

            d = MontyDecoder().decode(json_string)
            st.session_state.update(d)

            # Convert DataFrame back to original index after monty encode/decode
            data_df = st.session_state['saved_dataframe'].to_dict(orient='records')
            st.session_state['saved_dataframe'] = pd.DataFrame(data=data_df)

        else:
            st.warning(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Failed to load session: {e}")

## HELP 

dataframe_info = """
- `name` : Name of the defect, naming conventions described below.
- `charge` : Defect charge.
- `multiplicity` : Multiplicity in the unit cell.
- `energy_diff` : Energy of the defective cell minus the energy of the pristine cell in eV.
- `bulk_volume` : Pristine cell volume in $\\mathrm{\\AA^3}$

Defect naming: (element = $A$)
- Vacancy: `'Vac_A'` (symbol=$V_{A}$)
- Interstitial: `'Int_A'` (symbol=$A_{i}$)
- Substitution: `'Sub_B_on_A'` (symbol=$B_{A}$)
- Polaron: `'Pol_A'` (symbol=${A}_{A}$)
- DefectComplex: `'Vac_A;Int_A'` (symbol=$V_A - A_i$)
"""

file_loader_info = f"""
Load session file (`.defermi`) or dataset file (`.csv`,`.pkl` or `.json`)  

`defermi`:Restore previous saved session\n
`json`: Exported `DefectsAnalysis` object from the `python` library, not generated manually\n
`csv` or `pkl`: Rows are defect entries, columns are:
{dataframe_info}
"""

band_gap_info = """
Band gap and valence band maximum of the pristine material in eV. 
"""

dataset_info = f"""
Dataset containing defect entries (`pandas.DataFrame`).\n
Toggle **Include** to add or remove the defect entry from the calculations.\n
Rows are defect entries, columns are:\n
{dataframe_info}\n

Options:
- **Edit**: enter editing mode.
- **Reset**: restore the original dataset.
- **Save csv**: Save customized dataset as `csv` file.
"""