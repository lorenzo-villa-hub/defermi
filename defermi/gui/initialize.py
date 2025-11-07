
import tempfile
import os
import time
import json

import matplotlib
import streamlit as st

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
        cols = st.columns([0.4,0.6])
        with cols[0]:
            st.markdown('##### 📂 Load Session or Dataset')
        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(file_loader_info)
        init_state_variable('da',value=None)
        uploaded_file = st.file_uploader("upload", type=["defermi","csv","json","pkl"], on_change=reset_session, label_visibility="collapsed")

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


        cols = st.columns([0.1,0.1,0.7,0.1])
        with cols[0]:
            init_state_variable('edit_dataframe',value=False)
            edit_dataframe = st.checkbox('Edit',key='widget_edit_dataframe',value=st.session_state['edit_dataframe'])
            st.session_state['edit_dataframe'] = edit_dataframe

        with cols[1]:
            def reset_dataframes():
                for k in ['dataframe', 'df_complete','saved_dataframe']:
                    if k in st.session_state:
                        del st.session_state[k]
                st.session_state['edit_dataframe'] = False
                st.session_state['widget_edit_dataframe'] = False
                return 
            st.button('Reset',key='widget_reset_da',on_click=reset_dataframes)

        with cols[2]:
            csv_str = st.session_state.da.to_dataframe(include_data=False,include_structures=False).to_csv(index=False)
            filename = st.session_state['session_name'] + '_dataset.csv'
            st.download_button(
                label="💾 Save csv",
                data=csv_str,
                file_name=filename,
                mime="test/csv")   
        with cols[3]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(dataset_info)

        if st.session_state['edit_dataframe']:
            edited_df = st.data_editor(
                            st.session_state['df_complete'], 
                            column_config={
                                'Include':st.column_config.CheckboxColumn()
                            },
                            hide_index=True,
                            key='widget_data_editor')
            
            st.session_state['saved_dataframe'] = edited_df
            df_to_import = edited_df[edited_df["Include"] == True] # keep only selected rows
            st.session_state['dataframe'] = df_to_import

        else:
            st.session_state['df_complete'] = st.session_state['saved_dataframe']
            st.dataframe(st.session_state['saved_dataframe'],hide_index=True)

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
                d = json.load(f)
            d = MontyDecoder().decode(d)
            st.session_state.update(d)
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
- `bulk_volume` : Pristine cell volume in $\mathrm{\\AA^3}$

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
