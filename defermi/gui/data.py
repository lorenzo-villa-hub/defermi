
import streamlit as st

from defermi.gui.info import dataset_info
from defermi.gui.utils import init_state_variable, store_edited_df


def main():
    st.title("Data")
    st.set_page_config(layout="wide")

    if st.session_state.da:
        st.write('')
        cols = st.columns([0.1,0.7,0.1])
        with cols[0]:
            def reset_dataframes():
                for k in ['dataframe','complete_dataframe']:
                    if k in st.session_state:
                        del st.session_state[k]
                return 
            st.button('Reset',key='widget_reset_da',on_click=reset_dataframes)

        with cols[1]:
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
                        column_config={'Include':st.column_config.CheckboxColumn()},
                        hide_index=True,
                        num_rows='dynamic',
                        height='stretch',
                        key='widget_complete_dataframe',
                        on_change=store_edited_df,  # prevent double-clicking problem
                        args=['complete_dataframe'])
        
      #  edited_df = edited_df.dropna() # exclude rows with NaN
        st.session_state['complete_dataframe'] = edited_df
        if edited_df.empty:
            st.session_state['dataframe'] = None
        else:
            edited_df = edited_df.dropna()
            df_to_import = edited_df[edited_df["Include"] == True] # keep only selected rows
            st.session_state['dataframe'] = df_to_import

        st.session_state.pop('formation_energies_figure',None)
        
    else:
        st.warning('Dataset is empty')
    

if __name__ == '__main__':
    main()