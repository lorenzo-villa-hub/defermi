
import streamlit as st

from defermi.gui.main import pages_dict
from defermi.gui.inputs import upload_file, load_file
from defermi.gui.info import title
from defermi.gui.utils import init_state_variable, insert_space, load_session_from_preset, reset_session, widget_with_updating_state





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
        <div style='text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 1px;'>
            Welcome to the defermi UI!
            </span>
            <span style='font-weight: normal; font-size: 28px; margin-left: 10px;'>
                — A tool to analyse point-defects
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='text-align: center; font-size: 24px; color: #333333; margin-top: 10px;'>
            Load a file or a preset to get started
        </div>
        """,
        unsafe_allow_html=True
    )

    insert_space(100)
    cols = st.columns([0.7,0.3])
    with cols[0]:
        st.markdown('## 📄 Presets')
        init_state_variable('presets',value=None)
        options = ['Vacancies','Vacancies + Interstitial']

        def change_preset():
            widget_presets = st.session_state['widget_presets']
            st.session_state.clear()
            st.session_state['presets'] = widget_presets
            return


        st.markdown("""
            <style>
                .stMultiSelect [data-baseweb=select] span{
                    max-width: 1000px;
                    font-size: 1.0rem;
                }
            </style>
            """, unsafe_allow_html=True)
        try:
            presets = st.multiselect(
                                    label='presets',
                                    options=options,
                                    default=st.session_state['presets'],
                                    key='widget_presets',
                                    label_visibility='collapsed',
                                    max_selections=1,
                                    on_change=change_preset)
        except st.errors.StreamlitDuplicateElementKey: # catch duplicate key error on start-up, re-running the app make it disappear
            st.rerun()
        
        st.session_state['presets'] = presets

        preset = presets[0] if presets else None
        if preset and not st.session_state['session_loaded']:

            if preset == 'Vacancies':
                filename = 'vacancies.defermi'
                load_session_from_preset(filename=filename)

            if preset == 'Vacancies + Interstitial':
                filename = 'vacancies_interstitials.defermi'
                load_session_from_preset(filename=filename)

            st.session_state['session_loaded'] = True
            st.switch_page(pages_dict['overview'])  
        
            
        
if __name__ == '__main__':
    main()
