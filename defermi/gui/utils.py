
import io
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



def _filter_names(defect_names,key):

    names_key = f'names_{key}'
    init_state_variable(names_key,value=defect_names)
    init_state_variable(f'previous_names_{key}',value=defect_names)
    default = st.session_state[names_key]
    for name in st.session_state[names_key]:
        if name not in defect_names:
            default = defect_names
            break
    for name in defect_names:
        if name not in st.session_state[f'previous_names_{key}']:
            default.append(name)
    names = widget_with_updating_state(function=st.multiselect, key=names_key,label='Names',
                                    options=defect_names, default=default)
    st.session_state[f'previous_names_{key}'] = defect_names
    
    return names




def _filter_concentrations(defect_concentrations,key='brouwer'):

    output_key = f'output_{key}'
    init_state_variable(output_key,value='total')
    options = ['total','stable','all']
    index = options.index(st.session_state[output_key])
    output = widget_with_updating_state(function=st.radio,
                                        key=output_key,
                                        label='Concentrations style',
                                        options=options,
                                        index=index,
                                        horizontal=True)

    # select names
    conc_names = defect_concentrations.names
    names = _filter_names(defect_names=conc_names,key=key)

    # set consistent colors
    for idx,name in enumerate(names):
        if name not in st.session_state['color_dict'].keys():
            st.session_state['color_dict'][name] = st.session_state['color_sequence'][idx]
            for c in st.session_state['color_sequence']:
                if c not in st.session_state['color_dict'].values():
                    st.session_state['color_dict'][name] = c
                    break
    ordered_names = []
    for c in defect_concentrations.select_concentrations(names=names): # use plotting order
        if c.name not in ordered_names:
            ordered_names.append(c.name)
    colors = [st.session_state.color_dict[name] for name in ordered_names]

    # set charges and reset colors
    charges=None
    if output=='all':
        charges_key = f'charges_str_{key}'
        init_state_variable(charges_key,value=None)
        colors=None
        charges_str = st.text_input(label='Charges (q1,q2,...)',value=st.session_state[charges_key],key=f'widget_{charges_key}')
        st.session_state[charges_key] = charges_str
        if charges_str:
            charges = []
            for s in charges_str.split(','):
                charges.append(float(s))

    return output, names, charges, colors




def _get_axis_limits_with_widgets(label, key, default, boundaries):
    """
    Create widgets with axis limits that persist through session changes.
    Values are stored in `st.session_state`.

    Parameters
    ----------
    label : (str)
        Label to pass to widget.
    key : (str)
        String to pass to widget key.
    default : (tuple)
        Default value for axis limit.
    boundaries_ : tuple
        Max and min value for `st.slider` for axis.

    Returns
    -------
    set_lim : bool
        `st.checkbox` output for axis limit.
    lim : tuple
        `st.slider` output for axis limit.
    """
    lim_label = f'{label}_{key}'
    set_lim_label = 'set_'+ lim_label
    

    if set_lim_label not in st.session_state:
        st.session_state[set_lim_label] = False
    if lim_label not in st.session_state:
        st.session_state[lim_label] = default

    subcols = st.columns([0.3,0.7])
    with subcols[0]:
        set_lim = st.checkbox(label,value=st.session_state[set_lim_label],label_visibility='visible', key=f'widget_{set_lim_label}')
        st.session_state[set_lim_label] = set_lim
    with subcols[1]:
        disabled = not set_lim
        def update_default_lim(): 
            st.session_state[lim_label] = st.session_state[f'widget_{lim_label}']
        lim = st.slider(
                            label,
                            min_value=boundaries[0],
                            max_value=boundaries[1],
                            value=st.session_state[lim_label],
                            label_visibility='collapsed',
                            key=f'widget_{lim_label}',
                            disabled=disabled,
                            on_change=update_default_lim)  
        st.session_state[lim_label] = lim

    return set_lim, lim


def download_plot(fig,filename):
    # Convert the plot to PNG in memory
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf",bbox_inches='tight')
    buf.seek(0)

    filename = st.session_state['session_name'] + '_' + filename
    # Add a download button
    st.download_button(
        label="💾 Save plot",
        data=buf,
        file_name=filename,
        mime="pdf"
    )