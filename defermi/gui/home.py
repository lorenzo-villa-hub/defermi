import streamlit as st
import matplotlib.pyplot as plt

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
    if 'doping_diagram_figure' in st.session_state:
        fig = st.session_state['doping_diagram_figure']
        fig.gca().set_title('')
        subcols = st.columns([0.37,0.63])
        with subcols[1]:
            st.markdown('#### Doping Diagram')
        st.pyplot(fig, clear_figure=False, width="content")
    else:
        insert_space(530)

    

with cols[0]:
    st.write('')
    if 'brouwer_diagram_figure' in st.session_state:
        fig = st.session_state['brouwer_diagram_figure']
        fig.gca().set_title('')
        subcols = st.columns([0.35,0.65])
        with subcols[1]:
            st.markdown('#### Brouwer Diagram')
        st.pyplot(fig, clear_figure=False, width="content")

with cols[1]:
    st.write('')
    st.write('')

    doping_key, brouwer_key = 'fermi_level_doping_figure', 'fermi_level_brouwer_figure'
    if any([key in st.session_state for key in [doping_key,brouwer_key]]):
        init_state_variable('fermi_level_home_type',value='Doping')
        init_state_variable('fermi_level_home_figure',value=None)

        def get_fermi_level_figure(type):
            if type=='Brouwer' and brouwer_key in st.session_state:
                fig = st.session_state[brouwer_key]
                fig.gca().set_title('')
            elif type=='Doping' and doping_key in st.session_state:
                fig = st.session_state[doping_key]
                fig.gca().set_title('')
            return fig
        
        def update_fermi_level_figure():
            fig = get_fermi_level_figure(type=st.session_state['widget_fermi_level_home_type'])
            st.session_state['fermi_level_home_figure'] = fig
            return
        
        if not st.session_state['fermi_level_home_figure']:
            if doping_key in st.session_state:
                fig = get_fermi_level_figure(type='Doping')
            elif brouwer_key in st.session_state:
                fig = get_fermi_level_figure(type='Brouwer')
            st.session_state['fermi_level_home_figure'] = fig

        fig = st.session_state['fermi_level_home_figure']
        title = st.session_state['fermi_level_home_type']
        fig.gca().set_title('')
        subcols = st.columns([0.45,0.55])
        with subcols[1]:
            st.markdown(f'#### {title}')
        st.pyplot(fig, clear_figure=False, width="content")

        if all([key in st.session_state for key in [doping_key,brouwer_key]]):
            subcols = st.columns([0.3,0.7])
            with subcols[1]:
                options = ['Brouwer','Doping']
                index = options.index(st.session_state['fermi_level_home_type'])
                fermi_level_home_type = st.radio(
                                                "Select type",
                                                options=options,
                                                index=index,
                                                key='widget_fermi_level_home_type',
                                                on_change=update_fermi_level_figure,
                                                horizontal=True,
                                                label_visibility='hidden')            
                st.session_state['fermi_level_home_type'] = fermi_level_home_type

        elif doping_key in st.session_state and brouwer_key not in st.session_state:
            st.session_state['fermi_level_home_type'] = 'Doping'
        elif doping_key not in st.session_state and brouwer_key in st.session_state:
            st.session_state['fermi_level_home_type'] = 'Brouwer'






