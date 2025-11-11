
import os
import io

import streamlit as st

from defermi.gui.initialize import initialize, filter_entries, save_session
from defermi.gui.chempots import chempots
from defermi.gui.dos import dos
from defermi.gui.thermodynamics import thermodynamics
from defermi.gui.plotter import plotter
from defermi.gui.utils import init_state_variable

def main():
    st.set_page_config(layout="wide", page_title="defermi")


    st.markdown("""
    <style>
    /* Set sidebar max-width */
    [data-testid="stSidebar"] {
        width: 800px;
        min-width: 850px;
        max-width: 900px;
    }
    </style>
    """, unsafe_allow_html=True)
    #left_col, space1, middle_line, space2, right_col = st.columns([1.5, 0.05, 0.05,0.05, 1.7])
    middle_line, space2, right_col = st.columns([0.05,0.05, 1.7+1.55])

    with st.sidebar:
        cols = st.columns(2)
        with cols[0]:
            st.image(svg_logo,width=300)
            st.write('')
        with cols[1]:
            subcols = st.columns(2)
            with subcols[0]:
                pass
            with subcols[1]:
                init_state_variable('session_name',value='session')
                filename = st.session_state['session_name'] + '.defermi'
                save_session(filename)

        initialize()
        filter_entries()
        chempots()
        
        st.write('')
        st.divider()
        
        if st.session_state.da:
            cols = st.columns([0.05,0.95])
            with cols[0]:
                st.write('')
                init_state_variable('enable_thermodynamics',value=False)
                enable_thermodynamics = st.checkbox('Enable Thermodynamics', value=st.session_state['enable_thermodynamics'], 
                                                    key='widget_enable_thermodynamics',label_visibility='collapsed')
                st.session_state['enable_thermodynamics'] = enable_thermodynamics
            with cols[1]:
                st.markdown('# Thermodynamics')
            st.write('')
            if enable_thermodynamics:
                dos()
                thermodynamics()
    
    with middle_line:
        pass
        #st.markdown("<div style='border-left: 1px solid #999; height: 2000px; margin: auto;'></div>",unsafe_allow_html=True)

    with right_col:
        plotter()



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


if __name__ == "__main__":
    main()



