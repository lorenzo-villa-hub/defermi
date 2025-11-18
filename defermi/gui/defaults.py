
import streamlit as st
import seaborn as sns
import matplotlib
import pandas as pd

from defermi import DefectsAnalysis



def get_default_df():
    dtypes = {
        "Include": "boolean",
        "name": "string",
        "charge": "Int64",
        "multiplicity": "Int64",
        "energy_diff": "float64",
        "bulk_volume": "Int64"
    }
    df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in dtypes.items()})
    return df


def set_defaults():
    sns.set_theme(context='talk',style='whitegrid')

    st.session_state['fontsize'] = 16
    st.session_state['label_size'] = 16
    st.session_state['npoints'] = 80
    st.session_state['pressure_range'] = (1e-35,1e30)
    st.session_state['figsize'] = (8, 8)
    st.session_state['alpha'] = 0.0

    if "color_sequence" not in st.session_state:
        st.session_state['color_sequence'] = matplotlib.color_sequences['tab10']
        st.session_state['color_sequence'] += matplotlib.color_sequences['tab20']
        st.session_state['color_sequence'] += matplotlib.color_sequences['Pastel1']

    if st.session_state.da:
        df = st.session_state['complete_dataframe'].dropna()
        full_da = DefectsAnalysis.from_dataframe(
                                        df,
                                        band_gap=st.session_state.da.band_gap,
                                        vbm=st.session_state.da.vbm)
        st.session_state['color_dict'] = {name:st.session_state['color_sequence'][idx] for idx,name in enumerate(full_da.names)}
    return