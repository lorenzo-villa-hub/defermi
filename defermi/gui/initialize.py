
import tempfile
import os
import time

import matplotlib
import streamlit as st

from defermi import DefectsAnalysis 


def initialize():
    """
    Import dataframe file to initialize DefectsAnalysis object
    """
    if "color_sequence" not in st.session_state:
        st.session_state.color_sequence = matplotlib.color_sequences['tab10']

    def reset_da():
        if "da" in st.session_state:
            st.session_state.da = None
        return

    subcol1, subcol2 = st.columns([1, 2.5])
    with subcol1:
        st.markdown("**Dataset**")
    with subcol2:
        uploaded_file = st.file_uploader("Upload", type=["csv","json","pkl"], on_change=reset_da, label_visibility="collapsed")

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        cols = st.columns(2)
        with cols[0]:
            band_gap = st.number_input("Band gap (eV)", value=None, step=0.1, placeholder="Enter band gap")
        with cols[1]:
            vbm = st.number_input("VBM (eV)", value=0.0, step=0.1)

        if "band_gap" not in st.session_state:
            st.session_state.band_gap = band_gap
        if "vbm" not in st.session_state:
            st.session_state.vbm = vbm

        if "band_gap" in st.session_state:
            if "da" not in st.session_state:
                st.session_state.da = DefectsAnalysis.from_file(tmp_path, band_gap=band_gap, vbm=vbm)
            if not "color_dict" in st.session_state:
                st.session_state.color_dict = {name:st.session_state.color_sequence[idx] for idx,name in enumerate(st.session_state.da.names)}
            # clean up the temp file
            os.unlink(tmp_path)

            if 'init' not in st.session_state:
                # message disappears after 1 second 
                msg = st.empty()
                msg.success("Dataset initialized")
                time.sleep(1)
                msg.empty()
                st.session_state.init = True



def filter_entries():
    """
    GUI elements to filter defect entries in DefectsAnalysis
    """
    if "da" in st.session_state:
        if st.session_state.da:
            st.session_state.original_da = st.session_state.da.copy()
            st.markdown('**Filter entries**')
            cols = st.columns([0.11,0.15,0.25,0.22,0.28])
            with cols[0]:
                mode = st.radio("Mode",options=["and","or"], index=0)
            with cols[1]:
                exclude = st.checkbox("Exclude",value=False)
            with cols[2]:
                defect_types = []
                for entry in st.session_state.original_da:
                    dtype = entry.defect.type
                    if dtype not in defect_types:
                        defect_types.append(dtype)
                types = st.multiselect("types",defect_types,default=None)
            with cols[3]:
                defect_elements = st.session_state.da.elements
                elements = st.multiselect("elements",defect_elements,default=None)
            with cols[4]:
                defect_names = st.session_state.da.names
                names = st.multiselect("names",defect_names,default=None)

            st.session_state.da = st.session_state.original_da.filter_entries(
                                                                    inplace=False,
                                                                    mode=mode,
                                                                    exclude=exclude,
                                                                    types=types,
                                                                    elements=elements,
                                                                    names=names)

            df = st.session_state.da.table(display=['energy_diff']).drop('delta atoms',axis=1)
            st.dataframe(df)