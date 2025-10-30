
import tempfile
import os
import time
import json

import matplotlib
import streamlit as st

from monty.json import jsanitize, MontyEncoder, MontyDecoder

from defermi import DefectsAnalysis 
from defermi.gui.utils import init_state_variable, widget_with_updating_state, dynamic_input_data_editor


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
        st.markdown('##### 📂 Load Session or Dataset')
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

        cols = st.columns(2)
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


        cols = st.columns([0.1,0.1,0.8])
        with cols[0]:
            init_state_variable('edit_dataframe',value=False)
            edit_dataframe = st.checkbox('Edit',key='widget_edit_dataframe',value=st.session_state['edit_dataframe'])
            st.session_state['edit_dataframe'] = edit_dataframe

        with cols[1]:
            def reset_dataframes():
                for k in ['dataframe', 'df_complete']:
                    if k in st.session_state:
                        del st.session_state[k]
                st.session_state['edit_dataframe'] = False
                st.session_state['widget_edit_dataframe'] = False
            st.button('Reset',key='widget_reset_da',on_click=reset_dataframes)

        with cols[2]:
            csv_str = st.session_state.da.to_dataframe(include_data=False,include_structures=False).to_csv(index=False)
            filename = st.session_state['session_name'] + '_dataset.csv'
            st.download_button(
                label="💾 Save csv",
                data=csv_str,
                file_name=filename,
                mime="test/csv")   

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
            st.dataframe(st.session_state['df_complete'],hide_index=True)

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



        # init_state_variable('mode',value='and')
        # init_state_variable('exclude',value=False)
        # init_state_variable('types',value=None)
        # init_state_variable('elements',value=None)
        # init_state_variable('names',value=None)


        # st.markdown('**Filter entries**')
        # cols = st.columns([0.11,0.25,0.22,0.28,0.15])
        # with cols[0]:
        #     index = 0 if st.session_state['mode'] == 'and' else 1
        #     mode = st.radio("Mode",options=["and","or"], index=index)
        #     st.session_state['mode'] = mode
        # with cols[1]:
        #     defect_types = []
        #     for entry in st.session_state['original_da']:
        #         dtype = entry.defect.type
        #         if dtype not in defect_types:
        #             defect_types.append(dtype)
        #     types = widget_with_updating_state(function=st.multiselect,key='types',widget_key='widget_types',label='Types',
        #                                           options=defect_types,default=st.session_state['types'])

        # with cols[2]:
        #     defect_elements = st.session_state['original_da'].elements
        #     elements = widget_with_updating_state(function=st.multiselect, key='elements',label='Elements',
        #                                              options=defect_elements, default=st.session_state['elements'])
        # with cols[3]:
        #     defect_names = st.session_state['original_da'].names
        #     names = widget_with_updating_state(function=st.multiselect, key='names',label='Names',
        #                                              options=defect_names, default=st.session_state['names'])
        # with cols[4]:
        #     exclude = widget_with_updating_state(function=st.checkbox, key='exclude',label='Exclude',value=st.session_state['exclude'])
        #     edit_dataset = st.checkbox('Edit',key='widget_edit_dataset',value=False)

        # try:
        #     selected_entries = st.session_state.original_da.select_entries(
        #                                                         inplace=False,
        #                                                         mode=mode,
        #                                                         exclude=exclude,
        #                                                         types=types,
        #                                                         elements=elements,
        #                                                         names=names)
        #  #   st.session_state['eform_names'] = st.session_state['da'].names
        # except AttributeError:
        #     st.warning('Dataset is empty')



        # if 'original_dataframe' not in st.session_state:
        #     df = st.session_state.da.to_dataframe(include_data=False,include_structures=False) 
        #     df['Include'] = [True for i in range(len(df))]
        #     cols = ['Include'] + [col for col in df.columns if col != 'Include']
        #     df = df[cols]
        #     st.session_state['original_dataframe'] = df