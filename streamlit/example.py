import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from defermi import DefectsAnalysis
from defermi.plotter import plot_pO2_vs_fermi_level

sns.set_theme(context='talk',style='whitegrid')

fontsize = 18
label_size = 16
npoints = 100
pressure_range = (1e-35,1e25)
precursor_energy_pfu = -10

# ---- INPUT DATA ----
bulk_volume = 800  # Å³
data_dict = [
    {'name': 'Vac_O', 'charge': 2, 'multiplicity': 1, 'energy_diff': 7, 'bulk_volume': bulk_volume},
    {'name': 'Vac_Sr', 'charge': -2, 'multiplicity': 1, 'energy_diff': 8, 'bulk_volume': bulk_volume},
    {'name': 'Vac_O', 'charge': 0, 'multiplicity': 1, 'energy_diff': 10.8, 'bulk_volume': bulk_volume},
    {'name': 'Vac_Sr', 'charge': 0, 'multiplicity': 1, 'energy_diff': 7.8, 'bulk_volume': bulk_volume},
]

df = pd.DataFrame(data_dict)
band_gap = 2
vbm = 0
oxygen_ref = -5
da = DefectsAnalysis.from_dataframe(df, band_gap=band_gap, vbm=vbm)

# ---- PAGE CONFIG ----
st.set_page_config(layout="wide", page_title="defermi example")

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


st.title("`defermi` example")

# ---- LAYOUT ----
left_col, right_col = st.columns([0.7, 2.3])

# ---- LEFT COLUMN ----
with left_col:
    st.markdown("**Defect energies (eV)**")
    for idx,entry in enumerate(da.entries):
        den = entry.energy_diff
        range = (den-8,den+8)
        slider_label = entry.defect.name + ', q = ' + str(entry.defect.charge)
        new_energy = st.slider(slider_label, range[0], range[1], entry.energy_diff, 0.1, key=f"ed_entry{idx}")
        entry._energy_diff = new_energy

    st.markdown("**Chemical Potentials (eV)**")
    chempots = {
        'O': st.slider("μ(O)", -10.0, -5.0, -5.0, 0.1, key="muO"),
        'Sr': st.slider("μ(Sr)", -5.0, -1.0, -2.0, 0.1, key="muSr"),
    }

    st.markdown(r"**Effective Masses ($m^*/m_e$)**")
    dos = {
        'm_eff_e': st.slider("Electron", 0.1, 1.1, 0.5, 0.05, key="me"),
        'm_eff_h': st.slider("Hole",     0.1, 1.1, 0.4, 0.05, key="mh"),
    }

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
            st.pyplot(fig2, clear_figure=True, width="content")

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
                st.pyplot(fig3, clear_figure=True, width="content")

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
            st.pyplot(fig4, clear_figure=True, width="content")
