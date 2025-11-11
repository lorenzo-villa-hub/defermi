
import streamlit as st

from defermi.gui.utils import init_state_variable

st.title("Data")

if st.session_state.da:
    cols = st.columns([0.1,0.1,0.7,0.1])
    with cols[0]:
        init_state_variable('edit_dataframe',value=False)
        edit_dataframe = st.checkbox('Edit',key='widget_edit_dataframe',value=st.session_state['edit_dataframe'])
        st.session_state['edit_dataframe'] = edit_dataframe

    with cols[1]:
        def reset_dataframes():
            for k in ['dataframe', 'df_complete','saved_dataframe']:
                if k in st.session_state:
                    del st.session_state[k]
            st.session_state['edit_dataframe'] = False
            st.session_state['widget_edit_dataframe'] = False
            return 
        st.button('Reset',key='widget_reset_da',on_click=reset_dataframes)

    with cols[2]:
        csv_str = st.session_state.da.to_dataframe(include_data=False,include_structures=False).to_csv(index=False)
        filename = st.session_state['session_name'] + '_dataset.csv'
        st.download_button(
            label="💾 Save csv",
            data=csv_str,
            file_name=filename,
            mime="test/csv")   
    with cols[3]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            pass
            #st.write(dataset_info)

    if st.session_state['edit_dataframe']:
        edited_df = st.data_editor(
                        st.session_state['df_complete'], 
                        column_config={
                            'Include':st.column_config.CheckboxColumn()
                        },
                        hide_index=True,
                        num_rows='dynamic',
                        key='widget_data_editor')
        
        #st.write(edited_df)
        edited_df = edited_df.dropna() # exclude rows with NaN
        st.session_state['saved_dataframe'] = edited_df
        df_to_import = edited_df[edited_df["Include"] == True] # keep only selected rows
        st.session_state['dataframe'] = df_to_import

    else:
        st.session_state['df_complete'] = st.session_state['saved_dataframe']
        st.dataframe(st.session_state['saved_dataframe'],hide_index=True)

else:
    st.warning('Dataset is empty')