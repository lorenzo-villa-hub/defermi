import streamlit as st
import matplotlib.pyplot as plt

from defermi.gui.info import names_info
from defermi.gui.utils import download_plot, _filter_names, _get_axis_limits_with_widgets


def main():

    st.set_page_config(layout="wide")
    st.title("Binding Energies")

    if st.session_state.da:
        da = st.session_state.da
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
                                                        key='ctl',
                                                        default=(-0.5,da.band_gap+0.5),
                                                        boundaries=(-3.,da.band_gap+3.))
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
            fig = da.plot_binding_energies(
                names=names,
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
            st.pyplot(fig, clear_figure=False, width="content")

        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(names_info)
            st.write('')
            download_plot(fig=fig,filename='binding_energies.pdf')


if __name__ == '__main__':
    main()