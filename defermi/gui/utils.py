
import streamlit as st



def init_state_variable(key,value=None):
    if key not in st.session_state:
        st.session_state[key] = value


def widget_with_updating_state(function, key, widget_key=None, **kwargs):
    """
    Create widget with updating default values by using st.session_state

    Parameters
    ----------
    function : function
        Function to use as widget.
    key : str
        Key for st.session_state dictionary.
    widget_key : str
        Key to assign to widget. If None, 'widget_{key}' is used.
    kwargs : dict
        Kwargs to pass to widget function. 'on_change' and 'key' kwargs 
        are set by default.

    Returns
    -------
    var : 
        Output of widget function.
    """
    widget_key = widget_key or 'widget_' + key
    def update_var():
        st.session_state[key] = st.session_state[widget_key]
    
    if 'on_change' not in kwargs:
        kwargs['on_change'] = update_var
    kwargs['key'] = widget_key

    var = function(**kwargs)
    st.session_state[key] = var
    return var