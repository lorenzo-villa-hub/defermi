import streamlit as st
import matplotlib.pyplot as plt

from defermi.gui.brouwer import get_pO2_vs_fermi_level_figure
from defermi.gui.ctls import CTLsPlotter
from defermi.gui.doping import get_doping_vs_fermi_level_figure
from defermi.gui.formation_energies import FormationEnergiesPlotter
from defermi.gui.utils import svg_logo, init_state_variable, insert_space


st.set_page_config(layout="wide")
cols = st.columns(3)
with cols[1]:
    st.image(svg_logo,width=300)

st.divider()
cols = st.columns(2)
with cols[0]:
    fig = None
    if 'formation_energies_figure' in st.session_state:
        fig = st.session_state['formation_energies_figure']
    elif st.session_state.da:
        plotter = FormationEnergiesPlotter(st.session_state.da) 
        entries,colors = plotter.get_entries_and_colors(filter_names=False)
        fig = plotter.get_figure(entries,colors)
    if fig:
        fig.gca().set_title('')
        subcols = st.columns([0.32,0.68])
        with subcols[1]:
            st.markdown('#### Formation Energies')
        st.pyplot(fig, clear_figure=False, width="content")

with cols[1]:
    fig = None
    if 'ctls_figure' in st.session_state:
        fig = st.session_state['ctls_figure']
    elif st.session_state.da:
        plotter = CTLsPlotter(st.session_state.da) 
        entries = plotter.get_entries(filter_names=False)
        fig = plotter.get_figure(entries)
    if fig:
        fig.gca().set_title('')
        subcols = st.columns([0.25,0.75])
        with subcols[1]:
            st.markdown('#### Charge Transition Levels')
        st.pyplot(fig, clear_figure=False, width="content")


with cols[0]:
    st.write('')
    if 'doping_diagram_figure' in st.session_state:
        fig = st.session_state['doping_diagram_figure']
        fig.gca().set_title('')
        subcols = st.columns([0.37,0.63])
        with subcols[1]:
            st.markdown('#### Doping Diagram')
        st.pyplot(fig, clear_figure=False, width="content")
    else:
        insert_space(530)

    

with cols[1]:
    insert_space(85)
    if 'brouwer_diagram_figure' in st.session_state:
        fig = st.session_state['brouwer_diagram_figure']
        fig.gca().set_title('')
        subcols = st.columns([0.35,0.65])
        with subcols[1]:
            st.markdown('#### Brouwer Diagram')
        st.pyplot(fig, clear_figure=False, width="content")






