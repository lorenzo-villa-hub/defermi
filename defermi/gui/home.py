import streamlit as st

st.title("Home")

cols = st.columns(2)

with cols[0]:
    if 'formation_energies_figure' in st.session_state:
        fig = st.session_state['formation_energies_figure']
        st.pyplot(fig, clear_figure=False, width="content")