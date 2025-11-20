
import os
import io

import streamlit as st
import seaborn as sns
import matplotlib
import time

from defermi import DefectsAnalysis
from defermi.gui.defaults import set_defaults
from defermi.gui.initialize import initialize_state_variables, initialize_defects_analysis, initialize_complete_dataframe
from defermi.gui.inputs import upload_file, band_gap_vbm_inputs, load_file#, filter_entries
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
# from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable, save_session




pages_dict = {
    'home': st.Page('home.py',title='Home',icon=':material/home:'),
    'overview': st.Page('overview.py',title='Overview',icon=':material/view_module:'),
    'data': st.Page('data.py',title='Data',icon=':material/table:'), 
    'formation_energies': st.Page('formation_energies.py',title='Formation Energies',icon=':material/line_axis:'),  
    'doping': st.Page('doping.py',title='Doping',icon=':material/stacked_line_chart:'),
    'brouwer': st.Page('brouwer.py',title='Brouwer',icon=':material/ssid_chart:'),
    'fermi_level': st.Page('fermi_level.py',title='Fermi Level',icon=':material/show_chart:'),
    'ctls': st.Page('ctls.py',title='Charge Transition Levels',icon=':material/insert_chart:'),
    'binding_energies': st.Page('binding_energies.py',title='Binding Energies',icon=':material/stacked_line_chart:')     
}


with st.sidebar:
    file = upload_file()
    load_file(file)

    initialize_state_variables()
    initialize_complete_dataframe()
    initialize_defects_analysis(st.session_state['complete_dataframe'])

    band_gap_vbm_inputs()
    st.divider()

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

filename = st.session_state['session_name'] + '.defermi'
save_session(filename)
page.run()




