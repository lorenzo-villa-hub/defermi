
import io
import os
import streamlit as st
import json
import pandas as pd

from monty.json import jsanitize, MontyEncoder, MontyDecoder

import defermi.gui


def init_state_variable(key,value=None):
    if key not in st.session_state:
        st.session_state[key] = value

def reset_session():
    st.session_state.clear()
    return

def insert_space(px=20):
    """Insert vertical space in pixels."""
    st.markdown(f"<div style='margin-top:{px}px;'></div>", unsafe_allow_html=True)


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


def store_edited_df(key):
    """
    Update changes in a dataframe stored in session_state when using the data editor.
    Prevents double-clicking problem.
    """
    pkey = 'widget_' + key
    changes = st.session_state[pkey]
    df = st.session_state[key]

    for row in changes['added_rows']:
        df.loc[df.shape[0]] = row
        df = df.reset_index(drop=True)

    for row, edit in changes['edited_rows'].items(): # Apply edits
        for column, new_value in edit.items():
            df.loc[row, column] = new_value

    df = df.drop(changes['deleted_rows']) # Remove deleted rows
    st.session_state[key] = df            # Store the dataframe in the session key
    return


def get_session_data():
    data = {k:v for k,v in st.session_state.items() if 'widget' not in k and 'figure' not in k}
    keys_to_delete = [
        'session_loaded',
        'session_name',
        'presets',
        'precursors',
        'external_defects',
        'input_dataframe'
    ]
    for k in keys_to_delete:
        data.pop(k,None)
    return data


def save_session(filename):
    """Save Streamlit session state to a JSON file."""
    try:
        data = get_session_data()
        d = MontyEncoder().encode(data)

        # convert to pretty JSON string
        json_str = json.dumps(d, indent=2)

        # create a downloadable button
        st.download_button(
            label="💾 Save Session",
            data=json_str,
            file_name=filename,
            mime="application/json"
        )
        
    except Exception as e:
        st.error(f"Failed to prepare session download: {e}")


def load_session(uploaded_file):
    """Load Streamlit session state from JSON file."""
    data_bytes = uploaded_file.getvalue() # file content as bytes
    data_str = data_bytes.decode('utf-8') # decode bytes to string (JSON text)
    json_str = json.loads(data_str)
    
    d = MontyDecoder().decode(json_str)
    st.session_state.update(d)

    # Convert DataFrame back to original index after monty encode/decode
    data_df = st.session_state['complete_dataframe'].to_dict(orient='records')
    st.session_state['complete_dataframe'] = pd.DataFrame(data=data_df)


def load_session_from_path(file_path):
    """Load Streamlit session state from JSON file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                json_str = json.load(f)
            
            d = MontyDecoder().decode(json_str)
            st.session_state.update(d)

            # Convert DataFrame back to original index after monty encode/decode
            data_df = st.session_state['complete_dataframe'].to_dict(orient='records')
            st.session_state['complete_dataframe'] = pd.DataFrame(data=data_df)
        else:
            st.warning(f"File not found: {file_path}")
    except Exception as e:
        st.error(f"Failed to load session: {e}")


def load_session_from_preset(filename):
    session_file = os.path.join(defermi.gui.__path__[0],'presets',filename)
    load_session_from_path(session_file)
    return


def reset_home_figures():
    keys = [
        'formation_energies_figure',
        'brouwer_diagram_figure',
        'doping_diagram_figure',
        'fermi_level_figure'
    ]
    for k in keys:
        st.session_state.pop(k,None)



def _filter_names(defect_names,key):

    names_key = f'names_{key}'
    init_state_variable(names_key,value=defect_names)
    if f'previous_names_{key}' not in st.session_state:
        st.session_state[f'previous_names_{key}'] = defect_names
        default = defect_names
    else:
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


svg_logo = """
<svg
   width="137.35327mm"
   height="26.927582mm"
   viewBox="0 0 137.35327 26.927582"
   version="1.1"
   id="svg5"
   inkscape:version="1.2.2 (b0a8486541, 2022-12-01)"
   sodipodi:docname="defermi_logo.svg"
   inkscape:export-filename="defermi_logo.png"
   inkscape:export-xdpi="300"
   inkscape:export-ydpi="300"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
  <sodipodi:namedview
     id="namedview7"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:showpageshadow="2"
     inkscape:pageopacity="0.0"
     inkscape:pagecheckerboard="0"
     inkscape:deskcolor="#d1d1d1"
     inkscape:document-units="mm"
     showgrid="false"
     inkscape:zoom="1.4793368"
     inkscape:cx="281.88306"
     inkscape:cy="61.176061"
     inkscape:window-width="3774"
     inkscape:window-height="1531"
     inkscape:window-x="0"
     inkscape:window-y="0"
     inkscape:window-maximized="1"
     inkscape:current-layer="layer1" />
  <defs
     id="defs2" />
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1"
     transform="translate(-35.33694,-51.548845)">
    <text
       xml:space="preserve"
       style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:37.7137px;line-height:125%;font-family:'Latin Modern Sans Quotation';-inkscape-font-specification:'Latin Modern Sans Quotation, Normal';font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal;text-align:start;letter-spacing:0px;word-spacing:0px;writing-mode:lr-tb;text-anchor:start;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.942845px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
       x="33.3004"
       y="78.099289"
       id="text113"><tspan
         sodipodi:role="line"
         id="tspan111"
         style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:37.7137px;font-family:'Latin Modern Sans Quotation';-inkscape-font-specification:'Latin Modern Sans Quotation, Normal';font-variant-ligatures:normal;font-variant-caps:normal;font-variant-numeric:normal;font-variant-east-asian:normal;fill:#000080;stroke-width:0.942845px"
         x="33.3004"
         y="78.099289">d<tspan
   style="fill:#800000"
   id="tspan285">ef</tspan>ermi</tspan></text>
  </g>
</svg>
"""