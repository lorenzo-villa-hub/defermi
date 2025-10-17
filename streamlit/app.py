
import tempfile
import os

import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from defermi import DefectsAnalysis
from defermi.tools.utils import get_object_from_json
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
precursor_energy_pfu = -10
band_gap = None
vbm=None

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
        uploaded_file = st.file_uploader("", type=["csv","json","pkl"], label_visibility="collapsed")

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
            # clean up the temp file
            os.unlink(tmp_path)
            st.success("DefectsAnalysis object initialized")


    if "da" in st.session_state:
        da = st.session_state.da
        st.dataframe(da.table(pretty=True))
        st.markdown("**Chemical Potentials (eV)**")
        mu_string = "μ"
        chempots = {}
        for el in da.elements:
            chempots[el] = st.number_input(f"{mu_string}({el})", value=0.0, max_value=0.0,step=0.5)

        st.markdown("**Density of states**")
        subcol3, subcol4 = st.columns([0.5, 0.5])
        with subcol3:
            dos_type = st.radio("",("m*","DOS"),horizontal=True,key="dos",index=0)
        with subcol4:
            if dos_type == "DOS":
                # Save the uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name


        # st.markdown(r"**Effective Masses ($m^*/m_e$)**")
        # dos = {
        #     'm_eff_e': st.slider("Electron", 0.1, 1.1, 0.5, 0.05, key="me"),
        #     'm_eff_h': st.slider("Hole",     0.1, 1.1, 0.4, 0.05, key="mh"),
        # }

        st.markdown("**Thermodynamic Parameters**")
        #precursor_energy_pfu = st.slider("Precursor energy/f.u. (eV)", -20.0, -6.0, -10.0, 0.1, key="prec")
        temperature = st.slider("Temperature (K)", 0, 1500, 1000, 50, key="temp")
        if temperature == 0:
            temperature = 0.1

        enable_quench = st.checkbox("Enable quenching", value=False, key="enable_quench")
        if enable_quench:
            quench_temperature = st.slider("Quench Temperature (K)", 200, 1500, 1000, 50, key="qt")
            quenched_species = st.radio(
                "Select quenched species",
                ("All", r"$V_O$", r"$V_{Sr}$"),
                horizontal=True,
                key="quenched_species",
                index=0,
            )
            if quenched_species == 'All':
                quenched_species = None
            elif quenched_species == r"$V_O$":
                quenched_species = ['Vac_O']
            elif quenched_species == r"$V_{Sr}$":
                quenched_species = ['Vac_Sr']
        else:
            quenched_species = None
            quench_temperature = None


        st.markdown("**Dopant Settings**")
        dopant_type = st.radio(
            "Select dopant",
            ("None", "Donor", "Acceptor"),
            horizontal=True,
            key="dtype",
            index=0,
        )

        if dopant_type != "None":
            log_conc = st.slider(r"log₁₀(concentration (cm⁻³))", 10.0, 22.0, 18.0, 0.5, key="logconc")
            dopant_concentration = 10 ** log_conc

        if dopant_type == "None":
            dopant = None
            external_defects = []
        elif dopant_type == "Donor":
            dopant = {'name': 'Sub_D_on_Sr', 'charge': 1, 'conc': dopant_concentration}
            external_defects = [dopant]
        else:
            dopant = {'name': 'Sub_A_on_Sr', 'charge': -1, 'conc': dopant_concentration}
            external_defects = [dopant]

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
                st.markdown("**Brouwer Diagram**")
                precursors = {'SrO': precursor_energy_pfu}
                fig2 = da.plot_brouwer_diagram(
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
                )
                fig2.grid()
                fig2.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                fig2.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                thermodata = da.thermodata
                st.pyplot(fig2, clear_figure=False, width="content")

            # 2nd row
            c3, c4 = st.columns(2)
            with c3:
                if dopant:
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

    