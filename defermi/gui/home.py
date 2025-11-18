
import streamlit as st

from defermi.gui.inputs import upload_file
from defermi.gui.info import title
from defermi.gui.utils import insert_space, load_session_from_preset, reset_session


def main():
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
    insert_space(100)

    st.markdown(
        """
        <div style='text-align: center; font-size: 32px; font-weight: bold;'>
            Welcome to defermi!
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='text-align: center; font-size: 24px;'>
            Load a file or a preset to get started
        </div>
        """,
        unsafe_allow_html=True
    )

    insert_space(100)
    #cols = st.columns([0.7,0.3])
    cols = st.columns([0.45,0.1,0.45])
    with cols[0]:
        upload_file()

    with cols[2]:
        options = ['Vacancies','Vacancy + Interstitial']
        st.markdown('## 📄 Presets')
        presets = st.multiselect('presets',options=options,default=None, label_visibility='collapsed',max_selections=1,on_change=reset_session)
        if presets:
            preset = presets[0]
            if preset == 'Vacancies':
                load_session_from_preset(filename='vacancies.defermi')
            st.rerun()

if __name__ == '__main__':
    main()
