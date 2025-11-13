
import matplotlib.pyplot as plt
import streamlit as st
from contextlib import nullcontext

from defermi.plotter import plot_pO2_vs_fermi_level, plot_variable_species_vs_fermi_level
from defermi.gui.utils import download_plot




st.set_page_config(layout="wide")
st.title('Fermi Level')

if st.session_state.da:
    da = st.session_state.da
    is_oxygen = 'O' in da.elements
    if is_oxygen:
        cols = st.columns(2)
        if 'brouwer_thermodata' in st.session_state:
            # xlim = st.session_state['xlim (log)_brouwer']
            # xlim = (float(10**xlim[0]) , float(10**xlim[1])) if st.session_state['set_xlim (log)_brouwer'] else st.session_state['pressure_range']
            # ylim = None


            with cols[0]:
                fig = st.session_state['fermi_level_brouwer_figure'] #_po2_vs_fermi_level_diagram(xlim,ylim)
                st.pyplot(fig, clear_figure=False, width='content')
                subcols = st.columns([0.4,0.6])
                with subcols[1]:
                    download_plot(fig=fig,filename='fermi_level_brouwer.pdf')

    if 'doping_thermodata' in st.session_state:
        if st.session_state['doping_thermodata'] and st.session_state['dopant']:
            # no subcolumn if there is no brouwer diagram section 
            context = context = cols[1] if is_oxygen else nullcontext()
            with context:
                fig = st.session_state['fermi_level_doping_figure']
                st.pyplot(fig, clear_figure=False, width='content')
                subcols = st.columns([0.4,0.6])
                with subcols[1]:
                    download_plot(fig=fig,filename='fermi_level_doping.pdf')

else:
    st.warning('Dataset is empty')