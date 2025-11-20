
import streamlit as st
import pandas as pd
import time

from defermi import DefectsAnalysis
from defermi.gui.info import dataset_info, names_info
from defermi.gui.utils import init_state_variable, store_edited_df



def main():
    st.title("Data")
    st.set_page_config(layout="wide")

    st.write('')
    cols = st.columns([0.1,0.7,0.1])
    with cols[0]:
        def reset_dataframes():
            st.session_state.pop('complete_dataframe',None)
            return 
        st.button('Reset',key='widget_reset_da',on_click=reset_dataframes)

    with cols[1]:
        if st.session_state.da:
            csv_str = st.session_state.da.to_dataframe(include_data=False,include_structures=False).to_csv(index=False)
            filename = st.session_state['session_name'] + '_dataset.csv'
            st.download_button(
                label="💾 Save csv",
                data=csv_str,
                file_name=filename,
                mime="test/csv")   
    with cols[2]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            pass
            st.write(dataset_info)

    data = st.session_state['complete_dataframe']
    edited_df = st.data_editor(
                    data, 
                    column_config={
                        'Include':st.column_config.CheckboxColumn(default=True),
                        'name':st.column_config.TextColumn(default='Vac_O',help=names_info),
                        'charge':st.column_config.NumberColumn(default=None),
                        'multiplicity':st.column_config.NumberColumn(default=None),
                        'energy_diff':st.column_config.NumberColumn(default=None),
                        'bulk_volume':st.column_config.NumberColumn(default=None),
                        },
                    hide_index=True,
                    num_rows='dynamic',
                    height='stretch',
                    key='widget_complete_dataframe',
                    on_change=store_edited_df,  # prevent double-clicking problem
                    args=['complete_dataframe'])
    

    st.session_state['complete_dataframe'] = edited_df
    st.session_state['dataframe'] = edited_df

    st.session_state.pop('formation_energies_figure',None)


if __name__ == '__main__':
    main()