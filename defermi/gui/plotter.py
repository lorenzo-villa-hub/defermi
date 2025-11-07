
import numpy as np
import io
import matplotlib.pyplot as plt
import seaborn as sns

import streamlit as st

from defermi.plotter import plot_pO2_vs_fermi_level, plot_variable_species_vs_fermi_level, plot_pO2_vs_concentrations, plot_variable_species_vs_concentrations
from defermi.gui.utils import init_state_variable, widget_with_updating_state

def plotter():

    sns.set_theme(context='talk',style='whitegrid')

    st.session_state.fontsize = 16
    st.session_state.label_size = 16
    st.session_state.npoints = 80
    st.session_state.pressure_range = (1e-35,1e30)
    st.session_state.figsize = (8, 8)
    st.session_state.fig_width_in_pixels = 700
    border = False

    init_state_variable('show_brouwer_diagram',value=False)
    init_state_variable('show_doping_diagram',value=False)

    
    if "brouwer_thermodata" not in st.session_state:
        st.session_state.brouwer_thermodata = None

    if st.session_state.da:

        st.session_state.da.sort_entries()
        if not "color_dict" in st.session_state:
            st.session_state['color_dict'] = {name:st.session_state.color_sequence[idx] for idx,name in enumerate(st.session_state.da.names)}

        all_plots_to_display = [
                        'Formation energies',
                        'Charge transition levels',
                        'Binding energies',
                        'Brouwer diagram',
                        'Doping diagram',
                        'Fermi level']
        default_plots_to_display = ['Formation energies','Brouwer diagram','Doping diagram','Fermi level']
        init_state_variable('plots_to_display',value=default_plots_to_display)

        cols = st.columns([0.95,0.05])
        with cols[0]:
            plots_to_display = widget_with_updating_state(function=st.multiselect,key='plots_to_display',
                                                      label='Display',options=all_plots_to_display,
                                                      default=st.session_state['plots_to_display'])
        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(display_info)

        with st.container(border=border):
            if 'Formation energies' in plots_to_display:
                formation_energies()
            if 'Charge transition levels' in plots_to_display:
                charge_transition_levels()
            if 'Binding energies' in plots_to_display:
                    if 'DefectComplex' in st.session_state.da.types:
                        binding_energies()
                    else:
                        st.warning('No defect complexes in entries')


        if st.session_state['enable_thermodynamics']:        
            with st.container(border=border):
                if 'Brouwer diagram' in plots_to_display:    
                    brouwer_diagram()
            with st.container(border=border):
                if 'Doping diagram' in plots_to_display:
                    doping_diagram()
            
            with st.container(border=border):
                if 'Fermi level' in plots_to_display:
                    cols = st.columns([0.05,0.95])
                    with cols[0]:
                        show_mue_diagram = st.checkbox("show_fermi_doping",value=False,label_visibility='collapsed')
                    with cols[1]:
                        st.markdown("<h3 style='font-size:24px;'>Electron chemical potential</h3>", unsafe_allow_html=True)
                    if show_mue_diagram:
                        fermi_level()


def formation_energies():

    fontsize = st.session_state['fontsize']
    label_size = st.session_state['label_size']
    npoints = st.session_state['npoints']
    pressure_range = st.session_state['pressure_range']
    figsize = st.session_state['figsize']
    fig_width_in_pixels = st.session_state['fig_width_in_pixels']

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
                set_xlim, xlim = _get_axis_limits_with_widgets(
                                                            label='xlim',
                                                            key='eform',
                                                            default=(-0.5,da.band_gap+0.5),
                                                            boundaries=(-3.,da.band_gap+3.)) 
                xlim = xlim if set_xlim else None

                set_ylim, ylim = _get_axis_limits_with_widgets(
                                                            label='ylim',
                                                            key='eform',
                                                            default=(-20.,30.),
                                                            boundaries=(-20.,30.))
                ylim = ylim if set_ylim else None

                defect_names = da.names
                names = _filter_names(defect_names=defect_names,key='eform')

                entries = da.select_entries(names=names)
                colors = []
                ordered_names = []
                for entry in entries:
                    if entry.name not in ordered_names:
                        ordered_names.append(entry.name)      
                colors = [st.session_state.color_dict[name] for name in ordered_names]

            with cols[0]:
                fig1 = da.plot_formation_energies(
                    entries=entries,
                    chemical_potentials=st.session_state.chempots,
                    figsize=figsize,
                    fontsize=fontsize,
                    colors=colors,
                    xlim=xlim,
                    ylim=ylim)
                fig1.grid()
                fig1.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig1.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                st.pyplot(fig1, clear_figure=False, width="content")

            with cols[1]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(names_info)
                st.write('')                    
                download_plot(fig=fig1,filename='formation_energies.pdf')



def charge_transition_levels():

    fontsize = st.session_state['fontsize']
    label_size = st.session_state['label_size']
    npoints = st.session_state['npoints']
    pressure_range = st.session_state['pressure_range']
    figsize = st.session_state['figsize']
    fig_width_in_pixels = st.session_state['fig_width_in_pixels']

    if st.session_state.da and 'chempots' in st.session_state:
        da = st.session_state.da
        cols = st.columns([0.05,0.95])
        with cols[0]:
            show_formation_energies = st.checkbox("charge transition levels",value=True,label_visibility='collapsed')
        with cols[1]:
            st.markdown("<h3 style='font-size:24px;'>Charge transition levels</h3>", unsafe_allow_html=True)

        if show_formation_energies:
            cols = st.columns([0.7,0.3])
            with cols[1]:

                set_ylim, ylim = _get_axis_limits_with_widgets(
                                                            label='ylim',
                                                            key='ctl',
                                                            default=(-0.5,da.band_gap+0.5),
                                                            boundaries=(-3.,da.band_gap+3.))
                ylim = ylim if set_ylim else None

                defect_names = da.names
                names = _filter_names(defect_names=defect_names,key='ctl')

                entries = da.select_entries(names=names)

            with cols[0]:
                fig1 = da.plot_ctl(
                    entries=entries,
                    figsize=figsize,
                    fontsize=fontsize,
                    ylim=ylim)
                fig1.grid()
                fig1.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig1.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                st.pyplot(fig1, clear_figure=False, width="content")

            with cols[1]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(names_info)
                st.write('')
                download_plot(fig=fig1,filename='ctl.pdf')



def binding_energies():
    
    fontsize = st.session_state['fontsize']
    label_size = st.session_state['label_size']
    npoints = st.session_state['npoints']
    pressure_range = st.session_state['pressure_range']
    figsize = st.session_state['figsize']
    fig_width_in_pixels = st.session_state['fig_width_in_pixels']

    if st.session_state.da and 'chempots' in st.session_state:
        da = st.session_state.da
        colors = [st.session_state.color_dict[name] for name in da.names]
        cols = st.columns([0.05,0.95])
        with cols[0]:
            show_formation_energies = st.checkbox("binding energies",value=True,label_visibility='collapsed')
        with cols[1]:
            st.markdown("<h3 style='font-size:24px;'>Binding energies</h3>", unsafe_allow_html=True)

        if show_formation_energies:
            cols = st.columns([0.7,0.3])
            with cols[1]:
                set_xlim, xlim = _get_axis_limits_with_widgets(
                                                            label='xlim',
                                                            key='binding',
                                                            default=(-0.5,da.band_gap+0.5),
                                                            boundaries=(-3.,da.band_gap+3.)) 
                xlim = xlim if set_xlim else None

                set_ylim, ylim = _get_axis_limits_with_widgets(
                                                            label='ylim',
                                                            key='binding',
                                                            default=(-20.,30.),
                                                            boundaries=(-20.,30.))
                ylim = ylim if set_ylim else None
                
                complex_names = []
                for entry in da.select_entries(types=['DefectComplex']):
                    if entry.name not in complex_names:
                        complex_names.append(entry.name)
                names = _filter_names(defect_names=complex_names,key='binding')

                colors = [st.session_state.color_dict[name] for name in names]
                for color in st.session_state.color_sequence:
                    if color not in colors:
                        colors.append(color)

            with cols[0]:
                fig1 = da.plot_binding_energies(
                    names=names,
                    figsize=figsize,
                    fontsize=fontsize,
                    colors=colors,
                    xlim=xlim,
                    ylim=ylim)
                fig1.grid()
                fig1.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig1.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                st.pyplot(fig1, clear_figure=False, width="content")

            with cols[1]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(names_info)
                st.write('')
                download_plot(fig=fig1,filename='binding_energies.pdf')



def brouwer_diagram():

    if "dos" in st.session_state and "precursors" in st.session_state:
        if st.session_state['precursors']:
            fontsize = st.session_state['fontsize']
            label_size = st.session_state['label_size']
            npoints = st.session_state['npoints']
            pressure_range = st.session_state['pressure_range']
            figsize = st.session_state['figsize']
            fig_width_in_pixels = st.session_state['fig_width_in_pixels']

            da = st.session_state.da
            if "brouwer_da" not in st.session_state:
                st.session_state.brouwer_da = st.session_state.da
            brouwer_da = st.session_state.brouwer_da

            if brouwer_da:

                @st.cache_data
                def compute_brouwer_diagram():
                    brouwer_da.plot_brouwer_diagram(
                                            bulk_dos=st.session_state.dos,
                                            temperature=st.session_state.temperature,
                                            quench_temperature=st.session_state.quench_temperature,
                                            quenched_species=st.session_state.quenched_species,
                                            quench_elements = st.session_state.quench_elements,
                                            precursors=st.session_state.precursors,
                                            oxygen_ref=st.session_state.oxygen_ref,
                                            pressure_range=pressure_range,
                                            external_defects=st.session_state.external_defects,
                                            npoints=npoints
                                        )
                    return brouwer_da.thermodata

                cols = st.columns([0.05,0.25,0.15,0.55])
                with cols[0]:
                    show_brouwer_diagram = st.checkbox("brouwer diagram",value=True,label_visibility='collapsed')
                    st.session_state['show_brouwer_diagram'] = show_brouwer_diagram
                with cols[1]:
                    st.markdown("<h3 style='font-size:24px;'>Brouwer diagram</h3>", unsafe_allow_html=True)
                with cols[2]:
                    if st.button('Compute',key='widget_clear_cache_brouwer'):
                        compute_brouwer_diagram.clear()
                with cols[3]:
                    with st.popover(label='ℹ️',help='Info',type='tertiary'):
                        st.write(cache_info)

                if show_brouwer_diagram:
                    cols = st.columns([0.7,0.3])
                    with cols[1]:
                        default_xlim = int(np.log10(pressure_range[0])) , int(np.log10(pressure_range[1]))
                        set_xlim, xlim = _get_axis_limits_with_widgets(
                                                                    label='xlim (log)',
                                                                    key='brouwer',
                                                                    default=default_xlim,
                                                                    boundaries=default_xlim) 
                        xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                        xlim = xlim if set_xlim else pressure_range

                        set_ylim, ylim = _get_axis_limits_with_widgets(
                                                                    label='ylim (log)',
                                                                    key='brouwer',
                                                                    default=(-20,25),
                                                                    boundaries=(-50,30))
                        ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                        ylim = ylim if set_ylim else None   

                        brouwer_thermodata = compute_brouwer_diagram()
                        dc = brouwer_thermodata.defect_concentrations[0]
                        output, names, charges, colors = _filter_concentrations(dc,key='brouwer')

                    with cols[0]:  
                        #brouwer_thermodata = compute_brouwer_diagram()
                        fig2 = plot_pO2_vs_concentrations(
                                                    thermodata=brouwer_thermodata,
                                                    output=output,
                                                    figsize=figsize,
                                                    fontsize=fontsize,
                                                    xlim=xlim,
                                                    ylim=ylim,
                                                    colors=colors,
                                                    names=names,
                                                    charges=charges)                                           

                        fig2.grid()
                        fig2.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                        fig2.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                        st.session_state['brouwer_thermodata'] = brouwer_thermodata
                        st.pyplot(fig2, clear_figure=False, width="content")

                    with cols[1]:
                        with st.popover(label='ℹ️',help='Info',type='tertiary'):
                            st.write(concentrations_mode_info)
                        st.write('')
                        download_plot(fig=fig2,filename='brouwer_diagram.pdf')



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

            @st.cache_data
            def compute_doping_diagram():
                da.plot_doping_diagram(
                        variable_defect_specie=st.session_state.dopant,
                        concentration_range=st.session_state.conc_range,
                        chemical_potentials=st.session_state.chempots,
                        bulk_dos=st.session_state.dos,
                        temperature=st.session_state.temperature,
                        quench_temperature=st.session_state.quench_temperature,
                        quenched_species=st.session_state.quenched_species,
                        external_defects=st.session_state.external_defects,
                        npoints=npoints,
                        )
                return da.thermodata
            
            cols = st.columns([0.05,0.25,0.15,0.55])
            with cols[0]:
                show_doping_diagram = st.checkbox("doping diagram",value=True,label_visibility='collapsed')
                st.session_state['show_doping_diagram'] = show_doping_diagram
            with cols[1]:
                st.markdown("<h3 style='font-size:24px;'>Doping diagram</h3>", unsafe_allow_html=True)
            with cols[2]:
                if st.button('Compute',key='widget_clear_cache_doping'):
                    compute_doping_diagram.clear()
            with cols[3]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(cache_info)

            if show_doping_diagram:
                cols = st.columns([0.7,0.3])
                with cols[1]:
                    default_xlim = int(np.log10(conc_range[0])) , int(np.log10(conc_range[1]))
                    set_xlim, xlim = _get_axis_limits_with_widgets(
                                                                label='xlim (log)',
                                                                key='doping',
                                                                default=default_xlim,
                                                                boundaries=default_xlim) 
                    xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                    xlim = xlim if set_xlim else conc_range

                    set_ylim, ylim = _get_axis_limits_with_widgets(
                                                                label='ylim (log)',
                                                                key='doping',
                                                                default=(-20,25),
                                                                boundaries=(-50,30))
                    ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                    ylim = ylim if set_ylim else None   

                    doping_thermodata = compute_doping_diagram()
                    dc = doping_thermodata.defect_concentrations[0]
                    output, names, charges, colors = _filter_concentrations(dc,key='doping')

                with cols[0]:
                    fig3 = plot_variable_species_vs_concentrations(
                                                    doping_thermodata,
                                                    output=output,
                                                    figsize=figsize,
                                                    fontsize=fontsize,
                                                    colors=colors,
                                                    xlim=xlim,
                                                    ylim=ylim,
                                                    names=names,
                                                    charges=charges
                                                    )
                    fig3.grid()
                    fig3.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig3.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    st.session_state['doping_thermodata'] = doping_thermodata
                    st.pyplot(fig3, clear_figure=False, width="content")

                with cols[1]:
                    with st.popover(label='ℹ️',help='Info',type='tertiary'):
                        st.write(concentrations_mode_info)
                    st.write('')
                    download_plot(fig=fig3,filename='doping_diagram.pdf')


def fermi_level():
    pressure_range = st.session_state['pressure_range']
    da = st.session_state.da

    cols = st.columns(2)
    if 'brouwer_thermodata' in st.session_state and st.session_state['show_brouwer_diagram']:
        xlim = st.session_state['xlim (log)_brouwer']
        xlim = (float(10**xlim[0]) , float(10**xlim[1])) if st.session_state['set_xlim (log)_brouwer'] else pressure_range
        ylim = None

        with cols[0]:
            fig = _po2_vs_fermi_level_diagram(xlim,ylim)
            subcols = st.columns([0.4,0.6])
            with subcols[1]:
                download_plot(fig=fig,filename='fermi_level_brouwer.pdf')

    if 'doping_thermodata' in st.session_state and st.session_state['show_doping_diagram']:
        if st.session_state['doping_thermodata'] and st.session_state['dopant']:
            conc_range = st.session_state['conc_range']
            xlim = st.session_state['xlim (log)_doping']
            xlim = (float(10**xlim[0]) , float(10**xlim[1])) if st.session_state['set_xlim (log)_doping'] else conc_range
            ylim = None

            with cols[1]:
                fig = _doping_vs_fermi_level_diagram(xlim,ylim)
                subcols = st.columns([0.4,0.6])
                with subcols[1]:
                    download_plot(fig=fig,filename='fermi_level_doping.pdf')



def _po2_vs_fermi_level_diagram(xlim,ylim):
    if st.session_state['brouwer_thermodata']:    
        fontsize = st.session_state['fontsize']
        label_size = st.session_state['label_size']
        pressure_range = st.session_state['pressure_range']
        figsize = (6,6)

        da = st.session_state.da
        thermodata = st.session_state.brouwer_thermodata

        fig = plot_pO2_vs_fermi_level(
                partial_pressures=thermodata.partial_pressures,
                fermi_levels=thermodata.fermi_levels,
                band_gap=da.band_gap,
                figsize=figsize,
                fontsize=fontsize,
                xlim=xlim,
                ylim=ylim
        )
        fig.grid()
        fig.title('Brouwer diagram')
        fig.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
        fig.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
        st.pyplot(fig, clear_figure=False, width="content")
        return fig



def _doping_vs_fermi_level_diagram(xlim,ylim):
    if st.session_state['doping_thermodata']:    
        fontsize = st.session_state['fontsize']
        label_size = st.session_state['label_size']
        conc_range = st.session_state['conc_range']
        figsize = (6,6)

        da = st.session_state['da']
        thermodata = st.session_state['doping_thermodata']

        if type(st.session_state['dopant']) == dict:
            xlabel = st.session_state['dopant']['name']
        else:
            xlabel = st.session_state['dopant']

        fig = plot_variable_species_vs_fermi_level(
                xlabel = xlabel, 
                variable_concentrations=thermodata.variable_concentrations,
                fermi_levels=thermodata.fermi_levels,
                band_gap=da.band_gap,
                figsize=figsize,
                fontsize=fontsize,
                xlim=xlim,
                ylim=ylim
        )
        fig.grid()
        fig.title('Doping diagram')
        fig.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
        fig.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
        st.pyplot(fig, clear_figure=False, width="content")
        return fig


def _filter_names(defect_names,key):

    names_key = f'names_{key}'
    init_state_variable(names_key,value=defect_names)
    init_state_variable(f'previous_names_{key}',value=defect_names)
    default = st.session_state[names_key]
    for name in st.session_state[names_key]:
        if name not in defect_names:
            default = defect_names
            break
    for name in defect_names:
        if name not in st.session_state[f'previous_names_{key}']:
            default.append(name)
    names = widget_with_updating_state(function=st.multiselect, key=names_key,label='Names',
                                    options=defect_names, default=default)
    st.session_state[f'previous_names_{key}'] = defect_names
    
    return names




def _filter_concentrations(defect_concentrations,key='brouwer'):

    output_key = f'output_{key}'
    init_state_variable(output_key,value='total')
    options = ['total','stable','all']
    index = options.index(st.session_state[output_key])
    output = widget_with_updating_state(function=st.radio,
                                        key=output_key,
                                        label='Concentrations style',
                                        options=options,
                                        index=index,
                                        horizontal=True)

    # select names
    conc_names = defect_concentrations.names
    names = _filter_names(defect_names=conc_names,key=key)

    # set consistent colors
    for idx,name in enumerate(names):
        if name not in st.session_state['color_dict'].keys():
            st.session_state['color_dict'][name] = st.session_state['color_sequence'][idx]
            for c in st.session_state['color_sequence']:
                if c not in st.session_state['color_dict'].values():
                    st.session_state['color_dict'][name] = c
                    break
    ordered_names = []
    for c in defect_concentrations.select_concentrations(names=names): # use plotting order
        if c.name not in ordered_names:
            ordered_names.append(c.name)
    colors = [st.session_state.color_dict[name] for name in ordered_names]

    # set charges and reset colors
    charges=None
    if output=='all':
        charges_key = f'charges_str_{key}'
        init_state_variable(charges_key,value=None)
        colors=None
        charges_str = st.text_input(label='Charges (q1,q2,...)',value=st.session_state[charges_key],key=f'widget_{charges_key}')
        st.session_state[charges_key] = charges_str
        if charges_str:
            charges = []
            for s in charges_str.split(','):
                charges.append(float(s))

    return output, names, charges, colors




def _get_axis_limits_with_widgets(label, key, default, boundaries):
    """
    Create widgets with axis limits that persist through session changes.
    Values are stored in `st.session_state`.

    Parameters
    ----------
    label : (str)
        Label to pass to widget.
    key : (str)
        String to pass to widget key.
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


def download_plot(fig,filename):
    # Convert the plot to PNG in memory
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf",bbox_inches='tight')
    buf.seek(0)

    filename = st.session_state['session_name'] + '_' + filename
    # Add a download button
    st.download_button(
        label="💾 Save plot",
        data=buf,
        file_name=filename,
        mime="pdf"
    )


display_info = """
Select which plots to display. 

Options:
- **Formation energies**: Fermi level vs formation energies of defects. 
                        Only the charge state with lowest energy is shown. 
                        Stars represent charge transition levels.
- **Brouwer diagram**: Oxygen partial pressure vs concentrations of defects.
                    Only active if Brouwer diagram calculation has run.
- **Doping diagram**: Concentration of a target defect vs concentrations of all defects.
                    Only active if doping diagram calculation has run.
- **Fermi level**: Position of the equilibrium Fermi level (electron chemical potential) 
                vs oxygen partial pressure and variable defect concentration.
- **Charge transition level**: Position of the charge transition levels.
- **Binding energies**: Energy of the defect complex, minus the sum of the energies of the individual defects.
                        Only active if defect complexes are present in entries.
"""

cache_info = """
To prevent excessive lag when changing paramenters, the calculation result is cached. 
To rerun the calculation and regenerate the plot, click **Compute**.
"""

names_info = """
Select which defect entries to display in the plot based on `name`.
"""

concentrations_mode_info = """
Select style to plot concentrations and filter display of defect entries by `name`.

Options:
- **total**: Show the sum of concentrations in all charge states for each defect species.
- **stable**: Show the concentration of the most stable charge state for each defect species.
- **all**: Show the concentrations of all charge states for all defect species.
            Filter which charge states to show by typing them in the textbox.
"""