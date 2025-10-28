
import os
import io
import matplotlib

import streamlit as st

from defermi import DefectsAnalysis

from defermi.gui.initialize import initialize, filter_entries, save_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable

def main():
    st.set_page_config(layout="wide", page_title="defermi")

    left_col, right_col = st.columns([1.5, 1.8])

    with left_col:
        cols = st.columns(2)
        with cols[0]:
            st.title("`defermi`")

        da, mu = get_example_dataset()

        init_state_variable('session_name',value='example')
        init_state_variable('color_sequence',value = matplotlib.color_sequences['tab10'])
        init_state_variable('da',value=da)
        init_state_variable('band_gap',value=st.session_state.da.band_gap)
        init_state_variable('vbm',value=st.session_state.da.vbm)
        if not "color_dict" in st.session_state:
                st.session_state.color_dict = {name:st.session_state.color_sequence[idx] for idx,name in enumerate(st.session_state.da.names)}
        initialize(defects_analysis=da)
        filter_entries()
        
        init_state_variable('chempots',value=mu)
        chempots()
        
        st.write('')
        st.divider()
        st.write('')
        
        if st.session_state.da:
            cols = st.columns([0.05,0.95])
            with cols[0]:
                init_state_variable('enable_thermodynamics',value=False)
                enable_thermodynamics = st.checkbox('Enable Thermodynamics', value=st.session_state['enable_thermodynamics'], 
                                                    key='widget_enable_thermodynamics',label_visibility='collapsed')
                st.session_state['enable_thermodynamics'] = enable_thermodynamics
            with cols[1]:
                st.markdown('#### Thermodynamics')
            
            if enable_thermodynamics:
                dos()
                thermodynamics()
        
    with right_col:
        plotter()



def get_example_dataset():
    import pandas as pd
    from defermi import DefectsAnalysis

    bulk_volume = 800 # A^3

    energy_shift = 0
    data_dict = [
    {'name': 'Vac_O',
    'charge': 2,
    'multiplicity': 1,
    'energy_diff': 7 + energy_shift,
    'bulk_volume': bulk_volume},

    {'name': 'Vac_Sr',
    'charge': -2,
    'multiplicity': 1,
    'energy_diff': 8 + energy_shift,
    'bulk_volume': bulk_volume},

    {'name': 'Vac_O',
    'charge':0,
    'multiplicity':1,
    'energy_diff': 10.8 + energy_shift, 
    'bulk_volume': bulk_volume},

    {'name': 'Vac_Sr',
    'charge': 0,
    'multiplicity': 1,
    'energy_diff': 7.8 + energy_shift,
    'bulk_volume': bulk_volume},

    {'name': 'Sub_Fe_on_Sr',
    'charge': 0,
    'multiplicity': 1,
    'energy_diff': 2.5 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Sub_Fe_on_Sr',
    'charge': -1,
    'multiplicity': 1,
    'energy_diff': 3.9 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Sub_Fe_on_Ti',
    'charge': 1,
    'multiplicity': 1,
    'energy_diff': 7 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Sub_Fe_on_Ti',
    'charge': 2,
    'multiplicity': 1,
    'energy_diff': 6.5 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Sub_Fe_on_Ti-Vac_O',
    'charge': 0,
    'multiplicity': 1,
    'energy_diff': 14 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Sub_Fe_on_Ti-Vac_O',
    'charge': -1,
    'multiplicity': 1,
    'energy_diff': 15.3 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Int_O',
    'charge': -2,
    'multiplicity': 1,
    'energy_diff': 4 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Int_O',
    'charge': 0,
    'multiplicity': 1,
    'energy_diff': 3.5 + energy_shift,
    'bulk_volume':bulk_volume},

    {'name': 'Pol_Ti',
    'charge': -1,
    'multiplicity': 1,
    'energy_diff': 8 + energy_shift,
    'bulk_volume':bulk_volume},
    ]

    df = pd.DataFrame(data_dict)

    vbm = 0 # eV
    band_gap = 2 # eV
    da = DefectsAnalysis.from_dataframe(df,band_gap=band_gap,vbm=vbm)
    chempots = {'O': -5., 'Sr': -2., 'Fe':-5., 'Ti':-8.}
    return da, chempots



if __name__ == "__main__":
    main()