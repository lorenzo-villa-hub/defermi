
import streamlit as st

from defermi.gui.info import title

st.set_page_config(layout="wide")
cols = st.columns(3)
with cols[1]:
# Inject CSS that removes the border radius from the *next* st.image()
    st.markdown("""
    <style>
    /* Select the most recently created stImage (the last one) */
    [data-testid="stImage"] img {
        border-radius: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.image(title, width=300)

st.divider()