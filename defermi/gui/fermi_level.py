
import matplotlib.pyplot as plt
import streamlit as st
from contextlib import nullcontext

from defermi.plotter import plot_pO2_vs_fermi_level, plot_variable_species_vs_fermi_level
from defermi.gui.utils import download_plot



def _po2_vs_fermi_level_diagram(xlim,ylim,width='content'):
    if st.session_state['brouwer_thermodata']:    
        figsize = (6,6)
        da = st.session_state.da
        thermodata = st.session_state.brouwer_thermodata

        fig = plot_pO2_vs_fermi_level(
                partial_pressures=thermodata.partial_pressures,
                fermi_levels=thermodata.fermi_levels,
                band_gap=da.band_gap,
                figsize=figsize,
                fontsize=st.session_state['fontsize'],
                xlim=xlim,
                ylim=ylim
        )
        fig.grid()
        fig.title('Brouwer diagram')
        fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
        fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
        ax = fig.gca()
        fig = ax.get_figure()
        fig.patch.set_alpha(st.session_state['alpha'])
        ax.patch.set_alpha(st.session_state['alpha'])
        st.session_state['fermi_level_brouwer_figure'] = fig
        st.pyplot(fig, clear_figure=False, width=width)
        return fig



# def _doping_vs_fermi_level_diagram(xlim,ylim,width='content'):
#     if st.session_state['doping_thermodata']:    
#         figsize = (6,6)
#         da = st.session_state['da']
#         thermodata = st.session_state['doping_thermodata']

#         if type(st.session_state['dopant']) == dict:
#             xlabel = st.session_state['dopant']['name']
#         else:
#             xlabel = st.session_state['dopant']

#         fig = plot_variable_species_vs_fermi_level(
#                 xlabel = xlabel, 
#                 variable_concentrations=thermodata.variable_concentrations,
#                 fermi_levels=thermodata.fermi_levels,
#                 band_gap=da.band_gap,
#                 figsize=figsize,
#                 fontsize=st.session_state['fontsize'],
#                 xlim=xlim,
#                 ylim=ylim
#         )
#         fig.grid()
#         fig.title('Doping diagram')
#         fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
#         fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
#         ax = fig.gca()
#         fig = ax.get_figure()
#         fig.patch.set_alpha(st.session_state['alpha'])
#         ax.patch.set_alpha(st.session_state['alpha'])
#         st.session_state['fermi_level_doping_figure'] = fig
#         st.pyplot(fig, clear_figure=False, width=width)
#         return fig
    

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