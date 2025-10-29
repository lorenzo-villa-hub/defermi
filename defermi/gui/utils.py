
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


def dynamic_input_data_editor(data, key, **_kwargs):
    """
    Like streamlit's data_editor but which allows you to initialize the data editor with input arguments that can
    change between consecutive runs. Fixes the problem described here: https://discuss.streamlit.io/t/data-editor-not-changing-cell-the-1st-time-but-only-after-the-second-time/64894/13?u=ranyahalom
    :param data: The `data` argument you normally pass to `st.data_editor()`.
    :param key: The `key` argument you normally pass to `st.data_editor()`.
    :param _kwargs: All other named arguments you normally pass to `st.data_editor()`.
    :return: Same result returned by calling `st.data_editor()`
    """
    changed_key = f'{key}_khkhkkhkkhkhkihsdhsaskskhhfgiolwmxkahs'
    initial_data_key = f'{key}_khkhkkhkkhkhkihsdhsaskskhhfgiolwmxkahs__initial_data'

    def on_data_editor_changed():
        if 'on_change' in _kwargs:
            args = _kwargs['args'] if 'args' in _kwargs else ()
            kwargs = _kwargs['kwargs'] if 'kwargs' in _kwargs else  {}
            _kwargs['on_change'](*args, **kwargs)
        st.session_state[changed_key] = True

    if changed_key in st.session_state and st.session_state[changed_key]:
        data = st.session_state[initial_data_key]
        st.session_state[changed_key] = False
    else:
        st.session_state[initial_data_key] = data
    __kwargs = _kwargs.copy()
    __kwargs.update({'data': data, 'key': key, 'on_change': on_data_editor_changed})
    return st.data_editor(**__kwargs)