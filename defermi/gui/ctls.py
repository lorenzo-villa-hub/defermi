
import streamlit as st
import matplotlib.pyplot as plt

from defermi.gui.info import names_info
from defermi.gui.utils import download_plot, _filter_names, _get_axis_limits_with_widgets


class CTLsPlotter:

    def __init__(self,defects_analysis):
        self.da = defects_analysis

    def get_figure(self,entries=None,xlim=None,ylim=None):
        da = self.da
        fig = da.plot_ctl(
            entries=entries,
            figsize=st.session_state['figsize'],
            fontsize=st.session_state['fontsize'],
            ylim=ylim)
        fig.grid()
        fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
        fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
        ax = fig.gca()
        fig = ax.get_figure()
        fig.patch.set_alpha(st.session_state['alpha'])
        ax.patch.set_alpha(st.session_state['alpha'])
        st.session_state['ctls_figure'] = fig
        return fig
    
    def get_axis_limits(self):
        da = self.da
        set_xlim, xlim = _get_axis_limits_with_widgets(
                                                    label='xlim',
                                                    key='ctl',
                                                    default=(-0.5,da.band_gap+0.5),
                                                    boundaries=(-3.,da.band_gap+3.)) 
        xlim = xlim if set_xlim else None

        set_ylim, ylim = _get_axis_limits_with_widgets(
                                                    label='ylim',
                                                    key='ctl',
                                                    default=(-20.,30.),
                                                    boundaries=(-20.,30.))
        ylim = ylim if set_ylim else None
        return xlim,ylim


    def get_entries(self,filter_names=True):
        da = self.da
        defect_names = da.names
        if filter_names:
            names = _filter_names(defect_names=defect_names,key='ctl')
        else:
            names = defect_names
        entries = da.select_entries(names=names)
        return entries




def main():

    st.set_page_config(layout="wide")
    st.title("Charge Transition Levels")

    if st.session_state.da:
        da = st.session_state.da
        cols = st.columns([0.7,0.3])
        plotter = CTLsPlotter(defects_analysis=da)
        with cols[1]:
            xlim,ylim = plotter.get_axis_limits()
            entries = plotter.get_entries(da)

        with cols[0]:
            fig = plotter.get_figure(entries,xlim,ylim)
            st.pyplot(fig, clear_figure=False, width="stretch")

        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(names_info)
            st.write('')                    
            download_plot(fig=fig,filename='ctl.pdf')


if __name__ == '__main__':
    main()


