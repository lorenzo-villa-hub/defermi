
import os
import io
import json

import streamlit as st
import seaborn as sns
import matplotlib
from monty.json import jsanitize, MontyDecoder
import pandas as pd

import defermi
from defermi import DefectsAnalysis
from defermi.gui.inputs import main_inputs, filter_entries, band_gap_vbm_inputs, reset_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
# from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable, save_session


def load_session_from_example(file_path):
    """Load Streamlit session state from JSON file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                json_str = json.load(f)
            d = MontyDecoder().decode(json_str)
            st.session_state.update(d)

            # Convert DataFrame back to original index after monty encode/decode
            data_df = st.session_state['complete_dataframe'].to_dict(orient='records')
            st.session_state['complete_dataframe'] = pd.DataFrame(data=data_df)
        else:
            st.warning(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Failed to load session: {e}")


def set_defaults():
    sns.set_theme(context='talk',style='whitegrid')

    st.session_state['fontsize'] = 16
    st.session_state['label_size'] = 16
    st.session_state['npoints'] = 80
    st.session_state['pressure_range'] = (1e-35,1e30)
    st.session_state['figsize'] = (8, 8)
   # st.session_state['fig_width_in_pixels'] = 700
    st.session_state['alpha'] = 0.0

    if "color_sequence" not in st.session_state:
        st.session_state['color_sequence'] = matplotlib.color_sequences['tab10']
        st.session_state['color_sequence'] += matplotlib.color_sequences['tab20']
        st.session_state['color_sequence'] += matplotlib.color_sequences['Pastel1']

    if st.session_state.da:
        df = st.session_state['complete_dataframe'].dropna() # exclude rows with NaN
        st.session_state['dataframe'] = df[df["Include"] == True] # keep only selected rows
        full_da = DefectsAnalysis.from_dataframe(
                                        st.session_state['dataframe'],
                                        band_gap=st.session_state.da.band_gap,
                                        vbm=st.session_state.da.vbm)
        st.session_state['color_dict'] = {name:st.session_state['color_sequence'][idx] for idx,name in enumerate(full_da.names)}
    return


pages_dict = {
    'home': st.Page('home.py',title='Home',icon=':material/home:'),
    'data': st.Page('data.py',title='Data',icon=':material/table:'), 
    'formation_energies': st.Page('formation_energies.py',title='Formation Energies',icon=':material/line_axis:'),  
    'doping': st.Page('doping.py',title='Doping',icon=':material/stacked_line_chart:'),
    'brouwer': st.Page('brouwer.py',title='Brouwer',icon=':material/ssid_chart:'),
    'fermi_level': st.Page('fermi_level.py',title='Fermi Level',icon=':material/show_chart:'),
    'ctls': st.Page('ctls.py',title='Charge Transition Levels',icon=':material/insert_chart:'),
    'binding_energies': st.Page('binding_energies.py',title='Binding Energies',icon=':material/stacked_line_chart:')     
}


st.markdown("""
<style>
/* Set sidebar max-width */
[data-testid="stSidebar"] {
    width: 800px;
    min-width: 500;
    max-width: 900px;
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
   # main_inputs()
    init_state_variable('session_loaded',value=False)
    if not st.session_state['session_loaded']:
        session_file = os.path.join(defermi.gui.__path__[0],'app_example.defermi')
        load_session_from_example(session_file)
        st.session_state['session_loaded'] = True
    filter_entries()
    chempots()

    dos()
    thermodynamics()
    
set_defaults()

# exclude binding energies if there are no complexes
pages = []
for k,v in pages_dict.items():
    if k == 'binding_energies':
        if st.session_state.da:
            if 'DefectComplex' in st.session_state.da.types:
                pages.append(v)
    else:
        pages.append(v)

page = st.navigation(pages,expanded=True)
init_state_variable('session_name',value='session')
filename = st.session_state['session_name'] + '.defermi'
save_session(filename)
page.run()




