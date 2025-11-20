
import matplotlib.pyplot as plt
import streamlit as st
from contextlib import nullcontext

from defermi.plotter import plot_pO2_vs_fermi_level, plot_variable_species_vs_fermi_level
from defermi.gui.utils import download_plot


def main():

    st.set_page_config(layout="wide")
    st.title('Fermi Level')
    if st.session_state.da:
        da = st.session_state.da
        is_oxygen = 'O' in da.elements
        if is_oxygen:
            cols = st.columns(2)
            if 'brouwer_thermodata' in st.session_state:
                with cols[0]:
                    if 'fermi_level_brouwer_figure' in st.session_state:
                        fig = st.session_state['fermi_level_brouwer_figure'] #_po2_vs_fermi_level_diagram(xlim,ylim)
                        st.pyplot(fig, clear_figure=False, width='stretch')
                        subcols = st.columns([0.4,0.6])
                        with subcols[1]:
                            download_plot(fig=fig,filename='fermi_level_brouwer.pdf')
                    else:
                        st.warning('Brouwer diagram is not stored, compute it in the Brouwer section')

        if 'doping_thermodata' in st.session_state:
            if st.session_state['doping_thermodata'] and st.session_state['dopant']:
                # no subcolumn if there is no brouwer diagram section 
                context = context = cols[1] if is_oxygen else nullcontext()
                with context:
                    if 'fermi_level_doping_figure' in st.session_state:
                        fig = st.session_state['fermi_level_doping_figure']
                        st.pyplot(fig, clear_figure=False, width='stretch')
                        subcols = st.columns([0.4,0.6])
                        with subcols[1]:
                            download_plot(fig=fig,filename='fermi_level_doping.pdf')
                    else:
                        st.warning('Doping diagram is not stored, compute it in the Doping section')


if __name__ == '__main__':
    main()