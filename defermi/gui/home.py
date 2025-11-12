import streamlit as st
import matplotlib.pyplot as plt

from defermi.gui.formation_energies import FormationEnergiesPlotter
from defermi.gui.utils import svg_logo

#st.title("Home")
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
        fig.gca().set_title('Formation energies')
        st.pyplot(fig, clear_figure=False, width="content")


