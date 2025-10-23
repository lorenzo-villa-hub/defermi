
import streamlit as st

def init_state_variable(key,value=None):
    if key not in st.session_state:
        st.session_state[key] = value



def widget_with_updating_state(function, key, widget_key=None, **kwargs):

    widget_key = widget_key or 'widget_' + key
    def update_var():
        st.session_state[key] = st.session_state[widget_key]
    
    if 'on_change' not in kwargs:
        kwargs['on_change'] = update_var
    kwargs['key'] = widget_key

    var = function(**kwargs)
    st.session_state[key] = var
    return var
