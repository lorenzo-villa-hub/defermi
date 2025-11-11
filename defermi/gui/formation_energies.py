import streamlit as st
import matplotlib.pyplot as plt
import matplotlib

from defermi.gui.utils import init_state_variable, download_plot, _get_axis_limits_with_widgets, _filter_names


init_state_variable('alpha',value=0)

def get_formation_energies_figure(da,entries=None,colors=None):
    fig = da.plot_formation_energies(
        entries=entries,
        chemical_potentials=st.session_state.chempots,
        figsize=st.session_state['figsize'],
        fontsize=st.session_state['fontsize'],
        colors=colors,
        xlim=xlim,
        ylim=ylim)
    fig.grid()
    fig.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
    fig.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
    ax = fig.gca()
    fig = ax.get_figure()
    fig.patch.set_alpha(st.session_state['alpha'])
    ax.patch.set_alpha(st.session_state['alpha'])
    st.session_state['formation_energies_figure'] = fig
    return fig


def plot_options_widgets(da):
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

    return xlim,ylim,entries,colors



st.set_page_config(layout="wide")
fontsize = st.session_state['fontsize']
label_size = st.session_state['label_size']

if st.session_state.da and 'chempots' in st.session_state:
    da = st.session_state.da
    cols = st.columns([0.7,0.3])
    with cols[1]:
        xlim,ylim,entries,colors = plot_options_widgets(da)

    with cols[0]:
        fig = get_formation_energies_figure(da,entries,colors)
        st.pyplot(fig, clear_figure=False, width="content")

    with cols[1]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            pass#st.write(names_info)
        st.write('')                    
        download_plot(fig=fig,filename='formation_energies.pdf')

elif st.session_state.da and 'chempots' not in st.session_state:
    st.warning('Chemical potentials are not defined')
else:
    st.warning('Dataset is empty')





