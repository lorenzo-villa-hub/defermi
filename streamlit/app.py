
import tempfile
import os
import uuid

import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from monty.json import MontyDecoder
from pymatgen.core.composition import Composition

from defermi import DefectsAnalysis
from defermi.plotter import plot_pO2_vs_fermi_level

sns.set_theme(context='talk',style='whitegrid')


#da = DefectsAnalysis.from_dataframe(df, band_gap=band_gap, vbm=vbm)

# ---- PAGE CONFIG ----
st.set_page_config(layout="wide", page_title="defermi")

# ---- COMPACT GLOBAL STYLING ----
st.markdown("""
<style>
    .block-container {
        padding-top: 0.2rem;
        padding-bottom: 0rem;
        padding-left: 0.4rem;
        padding-right: 0.4rem;
        max-width: 85%;  /* keep slightly narrower than full width */
    }

    /* Reset labels and text to readable size */
    h1, h2, h3, h4, h5, label, .stSlider label, .stRadio label, .stSelectbox label, .stMarkdown {
        font-size: 0.85rem !important;
    }

    /* Reset sliders to normal size */
    div[data-baseweb="slider"] {
        transform: scale(1);
        transform-origin: left center;
        margin-bottom: 0;
    }

    /* Reset buttons to normal size */
    .stButton button {
        font-size: 0.9rem !important;
        padding: 0.2rem 0.4rem;
        height: auto !important;
    }

    /* Reset markdown paragraph text */
    div[data-testid="stMarkdownContainer"] p {
        font-size: 0.85rem !important;
        margin-bottom: 0.2rem !important;
    }

    .stRadio > div {
        gap: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("`defermi`")

fontsize = 18
label_size = 16
npoints = 100
pressure_range = (1e-35,1e25)
colors = matplotlib.color_sequences['tab10']


precursors = None
band_gap = None
vbm=None
dos = None
thermodata = None

oxygen_ref = -4.95

# ---- LAYOUT ----
left_col, right_col = st.columns([1.5, 1.8])

# ---- LEFT COLUMN ----
with left_col:
    # Other controls above ...

    # --- Inline dataset header + upload button ---
    subcol1, subcol2 = st.columns([1, 2.5])
    with subcol1:
        st.markdown("**Dataset**")
    with subcol2:
        uploaded_file = st.file_uploader("Upload", type=["csv","json","pkl"], label_visibility="collapsed")

    # --- Display dataset ---
    if uploaded_file is not None:

        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name

        st.markdown("**Band Structure Parameters**")
        vbm = st.number_input("VBM (eV)", value=0.0, step=0.1)
        band_gap = st.number_input("Band gap (eV)", value=None, step=0.1, placeholder="Enter band gap")

        if band_gap is not None:
            st.session_state.da = DefectsAnalysis.from_file(tmp_path, band_gap=band_gap, vbm=vbm)
            if not "color_dict" in st.session_state:
                st.session_state.color_dict = {name:colors[idx] for idx,name in enumerate(st.session_state.da.names)}
            # clean up the temp file
            os.unlink(tmp_path)
            st.success("DefectsAnalysis object initialized")


    if "da" in st.session_state:
        da = st.session_state.da
        st.dataframe(da.table())

        st.markdown("**Chemical Potentials (eV)**")
        mu_string = "μ"
        chempots = {}
        for el in da.elements:
            chempots[el] = st.number_input(f"{mu_string}({el})", value=0.0, max_value=0.0,step=0.5)

        st.markdown("**Density of states**")
        subcol3, subcol4 = st.columns([0.5, 0.5])
        with subcol3:
            dos_type = st.radio("Select",("$m^*/m_e$","DOS"),horizontal=True,key="dos",index=0,label_visibility='collapsed')
        with subcol4:
            if dos_type == "DOS":
                uploaded_dos = st.file_uploader("Upload", type=["json"], label_visibility="collapsed")
                if uploaded_dos is not None:
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                        tmp.write(uploaded_dos.getbuffer())
                        tmp_path = tmp.name
                        with open(tmp_path) as file:
                            dos = MontyDecoder().decode(file.read())
                    os.unlink(tmp_path)
            elif dos_type == '$m^*/m_e$':
                m_eff_e = st.number_input(f"e", value=1.0, max_value=1.1,step=0.1)
                m_eff_h = st.number_input(f"h", value=1.0, max_value=1.1,step=0.1)
                dos = {'m_eff_e':m_eff_e, 'm_eff_h':m_eff_h}

        st.markdown("**Thermodynamic Parameters**")
        temperature = st.slider("Temperature (K)", 0, 1500, 1000, 50, key="temp")
        if temperature == 0:
            temperature = 0.1


        st.markdown("**Precursors**")

        # Initialize session state
        if "precursor_entries" not in st.session_state:
            st.session_state.precursor_entries = []

        # Add new input
        if st.button("+ Add",key="add_precursor"):
            # Generate a unique ID for this entry
            entry_id = str(uuid.uuid4())
            st.session_state.precursor_entries.append({
                "id": entry_id,
                "composition": "",
                "energy": 0.0
            })

        def remove_precursor_entry(entry_id):
            for idx,entry in enumerate(st.session_state.precursor_entries):
                if entry['id'] == entry_id:
                    del st.session_state.precursor_entries[idx]


        # Render inputs
        for entry in st.session_state.precursor_entries:
            cols = st.columns([0.45, 0.45, 0.1])
            with cols[0]:
                entry["composition"] = st.text_input("Composition", value=entry["composition"], key=f"comp_{entry['id']}")
            with cols[1]:
                entry["energy"] = st.number_input("Energy p.f.u (eV)", value=entry["energy"], key=f"energy_{entry['id']}")
            with cols[2]:
                st.button("🗑️", on_click=remove_precursor_entry, args=[entry['id']], key=f"del_{entry['id']}")

        st.session_state.precursors = {
                            entry["composition"]: entry["energy"] 
                            for entry in st.session_state.precursor_entries
                            if entry["composition"]}


        elements_in_precursors = set()
        if st.session_state.precursors:
            for comp in st.session_state.precursors:
                if comp:
                    for element in Composition(comp).elements:
                        elements_in_precursors.add(element.symbol)

        filter_elements = set()
        for el in da.elements:
            if el in elements_in_precursors:
                filter_elements.add(el)
            else:
                st.warning(f'{el} missing from precursors')

        if filter_elements:
            if "brouwer_da" not in st.session_state:
                st.session_state.brouwer_da = da
            st.session_state.brouwer_da = da.filter_entries(elements=filter_elements)
            precursors = st.session_state.precursors


        enable_quench = st.checkbox("Enable quenching", value=False, key="enable_quench")
        if enable_quench:
            quench_temperature = st.slider("Quench Temperature (K)", 0, 1500, 1000, 50, key="qt")
            if quench_temperature == 0:
                quench_temperature = 0.1 

            
            quench_mode = st.radio("Quenching mode",("species","elements"),horizontal=True,key="quench_mode",index=0)

            if quench_mode == "species":
                species = [name for name in da.names]
                quenched_species = st.multiselect("Select quenched species",species,key="quenched_species",default=species)
        else:
            quenched_species = None
            quench_temperature = None


        st.markdown("**External Dopants**")

        if "external_defects_entries" not in st.session_state:
            st.session_state.external_defects_entries = []

        if st.button("+ Add",key="add_external_defect"):
            # Generate a unique ID for this entry
            entry_id = str(uuid.uuid4())
            st.session_state.external_defects_entries.append({
                "id": entry_id,
                "name": "",
                "charge": 0.0,
                "conc":0.0})

        def remove_external_defects_entries(entry_id):
            for idx,entry in enumerate(st.session_state.external_defects_entries):
                if entry['id'] == entry_id:
                    del st.session_state.external_defects_entries[idx]


        for defect in st.session_state.external_defects_entries:
            dcols = st.columns([0.3, 0.3, 0.3, 0.1])
            with dcols[0]:
                defect["name"] = st.text_input("Name", value=defect["name"], key=f"name_{defect['id']}")
            with dcols[1]:
                defect["charge"] = st.number_input("Charge", value=defect["charge"], key=f"charge_{defect['id']}")
            with dcols[2]:
                defect["conc"] = st.number_input("Concentration", value=defect["conc"], key=f"conc_{defect['id']}")
            with dcols[3]:
                st.button("🗑️", on_click=remove_external_defects_entries, args=[defect['id']], key=f"del_{defect['id']}")

        external_defects = [{
                            'name':e['name'],
                            'charge':e['charge'],
                            'conc':e['conc']
                            } for e in st.session_state.external_defects_entries]

        # if dopant_type != "None":
        #     log_conc = st.slider(r"log₁₀(concentration (cm⁻³))", 10.0, 22.0, 18.0, 0.5, key="logconc")
        #     dopant_concentration = 10 ** log_conc

        # if dopant_type == "None":
        #     dopant = None
        #     external_defects = []
        # elif dopant_type == "Donor":
        #     dopant = {'name': 'Sub_D_on_D', 'charge': 1, 'conc': dopant_concentration}
        #     external_defects = [dopant]
        # else:
        #     dopant = {'name': 'Pol_A', 'charge': -1, 'conc': dopant_concentration}
        #     external_defects = [dopant]

        run_button = st.button("Update Plots")


 # ---- RIGHT COLUMN (2×2 plots) ----
if "da" in st.session_state and band_gap:
    with right_col:
        figsize = (6, 6)
        if run_button or True:
            # 1st row
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Formation Energies**")
                fig1 = da.plot_formation_energies(
                    chemical_potentials=chempots,
                    figsize=figsize,
                    fontsize=fontsize)
                fig1.grid()
                fig1.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig1.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                st.pyplot(fig1, clear_figure=False, width="content")

            with c2:
                if dos and precursors:
                    if "brouwer_da" not in st.session_state:
                        st.session_state.brouwer_da = st.session_state.da
                    brouwer_da = st.session_state.brouwer_da
                    colors = [st.session_state.color_dict[name] for name in brouwer_da.names]
                    st.markdown("**Brouwer Diagram**")
                    fig2 = brouwer_da.plot_brouwer_diagram(
                        bulk_dos=dos,
                        temperature=temperature,
                        quench_temperature=quench_temperature,
                        quenched_species=quenched_species,
                        precursors=precursors,
                        oxygen_ref=oxygen_ref,
                        pressure_range=pressure_range,
                        external_defects=external_defects,
                        figsize=figsize,
                        fontsize=fontsize,
                        npoints=npoints,
                        colors=colors,
                    )
                    fig2.grid()
                    fig2.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig2.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    thermodata = da.thermodata
                    st.pyplot(fig2, clear_figure=False, width="content")

            # 2nd row
            c3, c4 = st.columns(2)
            with c3:
                if False:
                    if dos:
                        st.markdown("**Doping Diagram**")
                        dopant.pop('conc')
                        fig3 = da.plot_doping_diagram(
                            variable_defect_specie=dopant,
                            concentration_range=(1e10, 1e20),
                            chemical_potentials=chempots,
                            bulk_dos=dos,
                            temperature=temperature,
                            quench_temperature=quench_temperature,
                            quenched_species=quenched_species,
                            figsize=figsize,
                            fontsize=fontsize,
                            npoints=npoints
                        )
                        fig3.grid()
                        fig3.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                        fig3.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                        st.pyplot(fig3, clear_figure=False, width="content")

            with c4:
                if thermodata:
                    st.markdown("**Electron chemical potential**")
                    fig4 = plot_pO2_vs_fermi_level(
                            partial_pressures=thermodata.partial_pressures,
                            fermi_levels=thermodata.fermi_levels,
                            band_gap=da.band_gap,
                            figsize=figsize,
                            fontsize=fontsize,
                            xlim=pressure_range,
                    )
                    fig4.grid()
                    fig4.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig4.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    st.pyplot(fig4, clear_figure=False, width="content")

    