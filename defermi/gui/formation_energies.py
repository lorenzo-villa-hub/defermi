import streamlit as st
import matplotlib.pyplot as plt
import matplotlib

from defermi.gui.info import names_info
from defermi.gui.utils import init_state_variable, download_plot, _get_axis_limits_with_widgets, _filter_names


class FormationEnergiesPlotter:

    def __init__(self,defects_analysis):
        self.da = defects_analysis

    def get_figure(self,entries=None,colors=None,xlim=None,ylim=None):
        da = self.da
        if 'chempots' not in st.session_state:
            st.warning('Chemical potentials are not defined')
        fig = da.plot_formation_energies(
            entries=entries,
            chemical_potentials=st.session_state['chempots'],
            figsize=st.session_state['figsize'],
            fontsize=st.session_state['fontsize'],
            colors=colors,
            xlim=xlim,
            ylim=ylim)
        fig.grid()
        fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
        fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
        ax = fig.gca()
        fig = ax.get_figure()
        fig.patch.set_alpha(st.session_state['alpha'])
        ax.patch.set_alpha(st.session_state['alpha'])
        st.session_state['formation_energies_figure'] = fig
        return fig


    def get_axis_limits(self):
        da = self.da
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
        return xlim,ylim


    def get_entries_and_colors(self,filter_names=True):
        da = self.da
        defect_names = da.names
        if filter_names:
            names = _filter_names(defect_names=defect_names,key='eform')
        else:
            names = defect_names

        entries = da.select_entries(names=names)
        colors = []
        ordered_names = []
        for entry in entries:
            if entry.name not in ordered_names:
                ordered_names.append(entry.name)      
        colors = [st.session_state.color_dict[name] for name in ordered_names]

        return entries,colors


def main():
    st.set_page_config(layout="wide")
    st.title('Formation Energies')

    if st.session_state.da and 'chempots' in st.session_state:
        da = st.session_state.da
        cols = st.columns([0.7,0.3])
        plotter = FormationEnergiesPlotter(defects_analysis=da)
        with cols[1]:
            xlim,ylim = plotter.get_axis_limits()
            entries,colors = plotter.get_entries_and_colors(da)

        with cols[0]:
            fig = plotter.get_figure(entries,colors,xlim,ylim)
            st.pyplot(fig, clear_figure=False, width="content")

        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(names_info)
            st.write('')                    
            download_plot(fig=fig,filename='formation_energies.pdf')

if __name__ == '__main__':
    main()





