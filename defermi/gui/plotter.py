
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import streamlit as st

from defermi.plotter import plot_pO2_vs_fermi_level, plot_variable_species_vs_fermi_level


def plotter():

    run_button = st.button("Update Plots")

    sns.set_theme(context='talk',style='whitegrid')

    st.session_state.fontsize = 16
    st.session_state.label_size = 16
    st.session_state.npoints = 80
    st.session_state.pressure_range = (1e-35,1e30)
    st.session_state.figsize = (8, 8)
    st.session_state.fig_width_in_pixels = 700

    if "brouwer_thermodata" not in st.session_state:
        st.session_state.brouwer_thermodata = None

    if st.session_state.da:
        if run_button or True:
            formation_energies()            
            brouwer_diagram()
            po2_vs_fermi_level_diagram()
            doping_diagram()
            doping_vs_fermi_level_diagram()




def formation_energies():

    fontsize = st.session_state.fontsize
    label_size = st.session_state.label_size
    npoints = st.session_state.npoints
    pressure_range = st.session_state.pressure_range
    figsize = st.session_state.figsize
    fig_width_in_pixels = st.session_state.fig_width_in_pixels

    if st.session_state.da and 'chempots' in st.session_state:
        da = st.session_state.da
        cols = st.columns([0.05,0.95])
        with cols[0]:
            show_formation_energies = st.checkbox("formation energies",value=True,label_visibility='collapsed')
        with cols[1]:
            st.markdown("<h3 style='font-size:24px;'>Formation energies</h3>", unsafe_allow_html=True)

        if show_formation_energies:
            cols = st.columns([0.7,0.3])
            with cols[1]:
                set_xlim, xlim = get_axis_limits_with_widgets(
                                                            label='xlim',
                                                            key='eform',
                                                            default=(-0.5,da.band_gap+0.5),
                                                            boundaries=(-3.,da.band_gap+3.)) 
                xlim = xlim if set_xlim else None

                set_ylim, ylim = get_axis_limits_with_widgets(
                                                            label='ylim',
                                                            key='eform',
                                                            default=(-20.,30.),
                                                            boundaries=(-20.,30.))
                ylim = ylim if set_ylim else None
                
            with cols[0]:
                fig1 = da.plot_formation_energies(
                    chemical_potentials=st.session_state.chempots,
                    figsize=figsize,
                    fontsize=fontsize,
                    xlim=xlim,
                    ylim=ylim)
                fig1.grid()
                fig1.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig1.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                st.pyplot(fig1, clear_figure=False, width="content")






def brouwer_diagram():

    if "dos" in st.session_state and "precursors" in st.session_state:
        if st.session_state.precursors:
            fontsize = st.session_state.fontsize
            label_size = st.session_state.label_size
            npoints = st.session_state.npoints
            pressure_range = st.session_state.pressure_range
            figsize = st.session_state.figsize
            fig_width_in_pixels = st.session_state.fig_width_in_pixels

            da = st.session_state.da

            if "brouwer_da" not in st.session_state:
                st.session_state.brouwer_da = st.session_state.da
            brouwer_da = st.session_state.brouwer_da

            colors = [st.session_state.color_dict[name] for name in brouwer_da.names]
            for color in st.session_state.color_sequence:
                if color not in colors:
                    colors.append(color)

            cols = st.columns([0.05,0.95])
            with cols[0]:
                show_brouwer_diagram = st.checkbox("brouwer diagram",value=True,label_visibility='collapsed')
            with cols[1]:
                st.markdown("<h3 style='font-size:24px;'>Brouwer diagram</h3>", unsafe_allow_html=True)
            if show_brouwer_diagram:
                cols = st.columns([0.7,0.3])
                with cols[1]:
                    default_xlim = int(np.log10(pressure_range[0])) , int(np.log10(pressure_range[1]))
                    set_xlim, xlim = get_axis_limits_with_widgets(
                                                                label='xlim (log)',
                                                                key='brouwer',
                                                                default=default_xlim,
                                                                boundaries=default_xlim) 
                    xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                    xlim = xlim if set_xlim else pressure_range

                    set_ylim, ylim = get_axis_limits_with_widgets(
                                                                label='ylim (log)',
                                                                key='brouwer',
                                                                default=(-20,25),
                                                                boundaries=(-50,30))
                    ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                    ylim = ylim if set_ylim else None   

                with cols[0]:
                    fig2 = brouwer_da.plot_brouwer_diagram(
                        bulk_dos=st.session_state.dos,
                        temperature=st.session_state.temperature,
                        quench_temperature=st.session_state.quench_temperature,
                        quenched_species=st.session_state.quenched_species,
                        quench_elements = st.session_state.quench_elements,
                        precursors=st.session_state.precursors,
                        oxygen_ref=st.session_state.oxygen_ref,
                        pressure_range=pressure_range,
                        external_defects=st.session_state.external_defects,
                        figsize=figsize,
                        fontsize=fontsize,
                        npoints=npoints,
                        xlim=xlim,
                        ylim=ylim,
                        colors=colors,
                    )
                    fig2.grid()
                    fig2.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig2.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    st.session_state.brouwer_thermodata = brouwer_da.thermodata
                    st.pyplot(fig2, clear_figure=False, width="content")



def doping_diagram():

    if "dos" in st.session_state and "dopant" in st.session_state:
        if st.session_state.conc_range:
            fontsize = st.session_state.fontsize
            label_size = st.session_state.label_size
            npoints = st.session_state.npoints
            pressure_range = st.session_state.pressure_range
            figsize = st.session_state.figsize

            da = st.session_state.da
            conc_range = st.session_state.conc_range
            cols = st.columns([0.05,0.95])
            with cols[0]:
                show_doping_diagram = st.checkbox("doping diagram",value=True,label_visibility='collapsed')
            with cols[1]:
                st.markdown("<h3 style='font-size:24px;'>Doping diagram</h3>", unsafe_allow_html=True)
            if show_doping_diagram:
                cols = st.columns([0.7,0.3])
                with cols[1]:
                    default_xlim = int(np.log10(conc_range[0])) , int(np.log10(conc_range[1]))
                    set_xlim, xlim = get_axis_limits_with_widgets(
                                                                label='xlim (log)',
                                                                key='doping',
                                                                default=default_xlim,
                                                                boundaries=default_xlim) 
                    xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                    xlim = xlim if set_xlim else conc_range

                    set_ylim, ylim = get_axis_limits_with_widgets(
                                                                label='ylim (log)',
                                                                key='doping',
                                                                default=(-20,25),
                                                                boundaries=(-50,30))
                    ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                    ylim = ylim if set_ylim else None   

                with cols[0]:
                    fig3 = da.plot_doping_diagram(
                        variable_defect_specie=st.session_state.dopant,
                        concentration_range=st.session_state.conc_range,
                        chemical_potentials=st.session_state.chempots,
                        bulk_dos=st.session_state.dos,
                        temperature=st.session_state.temperature,
                        quench_temperature=st.session_state.quench_temperature,
                        quenched_species=st.session_state.quenched_species,
                        external_defects=st.session_state.external_defects,
                        figsize=figsize,
                        fontsize=fontsize,
                        npoints=npoints,
                        xlim=xlim,
                        ylim=ylim
                    )
                    fig3.grid()
                    fig3.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig3.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    st.session_state['doping_thermodata'] = da.thermodata
                    st.pyplot(fig3, clear_figure=False, width="content")



def po2_vs_fermi_level_diagram():
    
    if st.session_state.brouwer_thermodata:    
        fontsize = st.session_state.fontsize
        label_size = st.session_state.label_size
        pressure_range = st.session_state.pressure_range
        figsize = st.session_state.figsize

        da = st.session_state.da
        thermodata = st.session_state.brouwer_thermodata
        cols = st.columns([0.05,0.95])
        with cols[0]:
            show_mue_diagram = st.checkbox("mue diagram",value=False,label_visibility='collapsed',key='show_fermi_brouwer')
        with cols[1]:
            st.markdown("<h3 style='font-size:24px;'>Electron chemical potential</h3>", unsafe_allow_html=True)
        if show_mue_diagram:
            cols = st.columns([0.7,0.3])
            with cols[1]:
                default_xlim = int(np.log10(pressure_range[0])) , int(np.log10(pressure_range[1]))
                set_xlim, xlim = get_axis_limits_with_widgets(
                                                            label='xlim (log)',
                                                            key='fermi_brouwer',
                                                            default=default_xlim,
                                                            boundaries=default_xlim) 
                xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                xlim = xlim if set_xlim else pressure_range

                set_ylim, ylim = get_axis_limits_with_widgets(
                                                            label='ylim (log)',
                                                            key='fermi_brouwer',
                                                            default=(-0.5,da.band_gap+0.5),
                                                            boundaries=(-3.,da.band_gap+3.))
                ylim = ylim if set_ylim else None  
            with cols[0]:
                fig4 = plot_pO2_vs_fermi_level(
                        partial_pressures=thermodata.partial_pressures,
                        fermi_levels=thermodata.fermi_levels,
                        band_gap=da.band_gap,
                        figsize=figsize,
                        fontsize=fontsize,
                        xlim=xlim,
                        ylim=ylim
                )
                fig4.grid()
                fig4.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig4.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                st.pyplot(fig4, clear_figure=False, width="content")


def doping_vs_fermi_level_diagram():
    if 'doping_thermodata' in st.session_state:
        if st.session_state['doping_thermodata']:    
            fontsize = st.session_state['fontsize']
            label_size = st.session_state['label_size']
            conc_range = st.session_state['conc_range']
            figsize = st.session_state['figsize']

            da = st.session_state['da']
            thermodata = st.session_state['doping_thermodata']
            cols = st.columns([0.05,0.95])
            with cols[0]:
                show_mue_diagram = st.checkbox("show_fermi_doping",value=False,label_visibility='collapsed')
            with cols[1]:
                st.markdown("<h3 style='font-size:24px;'>Electron chemical potential</h3>", unsafe_allow_html=True)
            if show_mue_diagram:
                cols = st.columns([0.7,0.3])
                with cols[1]:
                    default_xlim = int(np.log10(conc_range[0])) , int(np.log10(conc_range[1]))
                    set_xlim, xlim = get_axis_limits_with_widgets(
                                                                label='xlim (log)',
                                                                key='fermi_doping',
                                                                default=default_xlim,
                                                                boundaries=default_xlim) 
                    xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                    xlim = xlim if set_xlim else conc_range

                    set_ylim, ylim = get_axis_limits_with_widgets(
                                                                label='ylim (log)',
                                                                key='fermi_doping',
                                                                default=(-0.5,da.band_gap+0.5),
                                                                boundaries=(-3.,da.band_gap+3.))
                    ylim = ylim if set_ylim else None
                with cols[0]:
                    fig4 = plot_variable_species_vs_fermi_level(
                            xlabel = st.session_state['dopant']['name'], 
                            variable_concentrations=thermodata.variable_concentrations,
                            fermi_levels=thermodata.fermi_levels,
                            band_gap=da.band_gap,
                            figsize=figsize,
                            fontsize=fontsize,
                            xlim=xlim,
                            ylim=ylim
                    )
                    fig4.grid()
                    fig4.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig4.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    st.pyplot(fig4, clear_figure=False, width="content")





def get_axis_limits_with_widgets(label, key, default, boundaries):
    """
    Create widgets with axis limits that persist through session changes.
    Values are stored in `st.session_state`.

    Parameters
    ----------
    plot_label : str
        Label to assign to `session_state` variables.
    axis_label : str
        Axis type ('x' or 'y').
    default : (tuple)
        Default value for axis limit.
    boundaries_ : tuple
        Max and min value for `st.slider` for axis.

    Returns
    -------
    set_lim : bool
        `st.checkbox` output for axis limit.
    lim : tuple
        `st.slider` output for axis limit.
    """
    lim_label = f'{label}_{key}'
    set_lim_label = 'set_'+ lim_label
    

    if set_lim_label not in st.session_state:
        st.session_state[set_lim_label] = False
    if lim_label not in st.session_state:
        st.session_state[lim_label] = default

    subcols = st.columns([0.3,0.7])
    with subcols[0]:
        set_lim = st.checkbox(label,value=st.session_state[set_lim_label],label_visibility='visible', key=f'widget_{set_lim_label}')
        st.session_state[set_lim_label] = set_lim
    with subcols[1]:
        disabled = not set_lim
        def update_default_lim(): 
            st.session_state[lim_label] = st.session_state[f'widget_{lim_label}']
        lim = st.slider(
                            label,
                            min_value=boundaries[0],
                            max_value=boundaries[1],
                            value=st.session_state[lim_label],
                            label_visibility='collapsed',
                            key=f'widget_{lim_label}',
                            disabled=disabled,
                            on_change=update_default_lim)  
        st.session_state[lim_label] = lim

    return set_lim, lim