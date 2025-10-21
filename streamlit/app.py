
import tempfile
import os
import uuid
import time

import numpy as np

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



# ---- PAGE CONFIG ----
st.set_page_config(layout="wide", page_title="defermi")


st.title("`defermi`")

fontsize = 16
label_size = 16
npoints = 80
pressure_range = (1e-35,1e25)
color_sequence = matplotlib.color_sequences['tab10']


precursors = None
band_gap = None
vbm=None
dos = None
thermodata = None
oxygen_ref = -4.95


left_col, right_col = st.columns([1.5, 1.8])

# ---- INPUTS 
with left_col:

#### INITIALIZE ####

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

        if band_gap is not None:
            st.session_state.da = DefectsAnalysis.from_file(tmp_path, band_gap=band_gap, vbm=vbm)
            if not "color_dict" in st.session_state:
                st.session_state.color_dict = {name:color_sequence[idx] for idx,name in enumerate(st.session_state.da.names)}
            # clean up the temp file
            os.unlink(tmp_path)

            if 'init' not in st.session_state:
                # message disappears after 1 second 
                msg = st.empty()
                msg.success("Dataset initialized")
                time.sleep(1)
                msg.empty()
                st.session_state.init = True

#### FILTER ENTRIES #####

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

            da = st.session_state.da
            df = da.table(display=['energy_diff']).drop('delta atoms',axis=1)
            st.dataframe(df)

#### CHEMICAL POTENTIALS #####

            st.markdown("**Chemical Potentials (eV)**")
            mu_string = "μ"
            if "chempots" not in st.session_state:    
                st.session_state.chempots = {}
            cols = st.columns(5)
            for idx,el in enumerate(da.elements):
                ncolumns = 5
                col_idx = idx%ncolumns
                with cols[col_idx]:
                    st.session_state.chempots[el] = st.number_input(f"{mu_string}({el})", value=0.0, max_value=0.0,step=0.5)

            st.divider()

#### DOS ####

            st.markdown("**Density of states**")
            subcol3, subcol4 = st.columns([0.5, 0.5])
            with subcol3:
                dos_type = st.radio("Select",("$m^*/m_e$","DOS"),horizontal=True,key="dos",index=0,label_visibility='collapsed')
            with subcol4:
                if dos_type == "DOS":
                    uploaded_dos = st.file_uploader("Upload", type=["json"], label_visibility="collapsed")
                    if uploaded_dos is not None:
                        # Save the uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                            tmp.write(uploaded_dos.getbuffer())
                            tmp_path = tmp.name
                            with open(tmp_path) as file:
                                dos = MontyDecoder().decode(file.read())
                        os.unlink(tmp_path)
                elif dos_type == '$m^*/m_e$':
                    cols = st.columns(2)
                    with cols[0]:
                        m_eff_e = st.number_input(f"e", value=1.0, max_value=1.1,step=0.1)
                    with cols[1]:
                        m_eff_h = st.number_input(f"h", value=1.0, max_value=1.1,step=0.1)
                    dos = {'m_eff_e':m_eff_e, 'm_eff_h':m_eff_h}

            if "dos" not in st.session_state:
                st.session_state.dos = dos

#### TEMPERATURE

            st.markdown("**Thermodynamic Parameters**")
            temperature = st.slider("Temperature (K)", 0, 1500, 1000, 50, key="temp")
            if temperature == 0:
                temperature = 0.1

#### PRECURSORS ####

            st.markdown("**Precursors**")

            # Initialize entries
            if "precursor_entries" not in st.session_state:
                st.session_state.precursor_entries = []
            
            cols = st.columns([0.1, 0.4, 0.4, 0.1])
            with cols[0]:
                if st.button("➕",key="add_precursor"):
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


            for entry in st.session_state.precursor_entries:
                with cols[1]:
                    entry["composition"] = st.text_input("Composition", value=entry["composition"], key=f"comp_{entry['id']}")
                with cols[2]:
                    entry["energy"] = st.number_input("Energy p.f.u (eV)", value=entry["energy"], step=1.0, key=f"energy_{entry['id']}")
                with cols[3]:
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
            missing_elements = set()
            for el in da.elements:
                if el in elements_in_precursors:
                    filter_elements.add(el)
                else:
                    missing_elements.add(el)

            cols = st.columns(5)
            for idx,el in enumerate(missing_elements):
                ncolumns = 5
                col_idx = idx%ncolumns
                with cols[col_idx]:
                    st.warning(f'{el} missing from precursors')

            if filter_elements:
                if "brouwer_da" not in st.session_state:
                    st.session_state.brouwer_da = da
                st.session_state.brouwer_da = da.filter_entries(elements=filter_elements)
                precursors = st.session_state.precursors

#### QUENCHING ####

            enable_quench = st.checkbox("Enable quenching", value=False, key="enable_quench")
            if enable_quench:
                quench_temperature = st.slider("Quench Temperature (K)", 0, 1500, 300, 50, key="qt")
                if quench_temperature == 0:
                    quench_temperature = 0.1 

                
                quench_mode = st.radio("Quenching mode",("species","elements"),horizontal=True,key="quench_mode",index=0)

                if "brouwer_da" in st.session_state:
                    if quench_mode == "species":
                        species = [name for name in st.session_state.brouwer_da.names]
                        quenched_species = st.multiselect("Select quenched species",species,key="quenched_species",default=species)
                        quench_elements = False
                    elif quench_mode == "elements":
                        species = set()
                        for entry in st.session_state.brouwer_da:
                            if entry.defect.type == 'Vacancy':
                                species.add(entry.defect.name)
                            else:
                                species.add(entry.defect.specie)
                        quenched_species = st.multiselect("Select quenched elements",species,key="quenched_species",default=species)
                        quench_elements = True
            else:
                quenched_species = None
                quench_elements = False
                quench_temperature = None

#### EXTERNAL DEFECTS ####

            st.markdown("**External defects**")

            if "external_defects_entries" not in st.session_state:
                st.session_state.external_defects_entries = []

            cols = st.columns([0.11, 0.26, 0.26, 0.26, 0.11])
            with cols[0]:
                if st.button("➕",key="add_external_defect"):
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
                with cols[1]:
                    defect["name"] = st.text_input("Name", key=f"name_{defect['id']}")
                with cols[2]:
                    defect["charge"] = st.number_input("Charge", step=1.0,key=f"charge_{defect['id']}")
                with cols[3]:
                    defect["conc"] = st.number_input(r"log₁₀(concentration (cm⁻³))", step=1.0, key=f"conc_{defect['id']}")
                    defect["conc"] = 10**defect["conc"]
                with cols[4]:
                    st.button("🗑️", on_click=remove_external_defects_entries, args=[defect['id']], key=f"del_{defect['id']}")

            external_defects = [{
                                'name':e['name'],
                                'charge':e['charge'],
                                'conc':e['conc']
                                } for e in st.session_state.external_defects_entries if e["name"]]

#### DOPANTS ####
     
            st.markdown("**Dopant settings**")
            possible_dopants = ["None","Donor","Acceptor"]
            for entry in da:
                if entry.defect.type == "Substitution":
                    el = entry.defect.specie
                    if el not in possible_dopants:
                        possible_dopants.append(el)
            possible_dopants.append('custom')
            dopant = st.radio("Select dopant",options=possible_dopants,index=0, horizontal=True)
            
            if dopant == "None":
                dopant = None
            elif dopant == "Donor":
                cols = st.columns(2)
                with cols[0]:
                    charge = st.number_input("Charge", min_value=0.0, value=1.0, step = 1.0, key="charge_dopant")
                with cols[1]:
                    min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="conc_range")
                conc_range = ( float(10**min_conc), float(10**max_conc) )
                dopant = {"name":"D","charge":charge}

            elif dopant == "Acceptor":
                cols = st.columns(2)
                with cols[0]:
                    charge = st.number_input("Charge", max_value=0.0, value=-1.0, step = 1.0, key="charge_dopant")
                with cols[1]:
                    min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="conc_range")
                conc_range = ( float(10**min_conc), float(10**max_conc) )
                dopant = {"name":"A","charge":charge}

            elif dopant == "custom":
                cols = st.columns(3)
                with cols[0]:
                    name = st.text_input("Name", key="name_dopant")
                with cols[1]:
                    charge = st.number_input("Charge", step=1.0,key="charge_dopant")
                with cols[2]:
                    min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="conc_range")
                conc_range = ( float(10**min_conc), float(10**max_conc) )
                dopant = {"name":name,"charge":charge}

            else:
                min_conc, max_conc = st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=(5, 18), key="conc_range")
                conc_range = ( float(10**min_conc), float(10**max_conc) )            


            run_button = st.button("Update Plots")


#----- PLOTS ----#

st.session_state.brouwer_thermodata = None
if "da" in st.session_state and band_gap:
    with right_col:
        figsize = (8, 8)
        fig_width_in_pixels = 700
        if run_button or True:

#### FORMATION ENERGIES ####

            cols = st.columns([0.05,0.95])
            with cols[0]:
                show_formation_energies = st.checkbox("formation energies",value=True,label_visibility='collapsed')
            with cols[1]:
                st.markdown("<h3 style='font-size:24px;'>Formation energies</h3>", unsafe_allow_html=True)

            if show_formation_energies:
                cols = st.columns([0.7,0.3])
                with cols[1]:
                    vbm = st.session_state.da.vbm
                    cbm = vbm + st.session_state.da.band_gap
                    subcols = st.columns([0.3,0.7])
                    with subcols[0]:
                        set_xlim = st.checkbox("xlim",value=False,label_visibility='visible', key='set_xlim_eform')
                    with subcols[1]:
                        xlim = st.slider("xlim", min_value=-3.,max_value=cbm+3.,value=(-0.5,cbm+0.5),label_visibility='collapsed', key='xlim_eform')
                    xlim = xlim if set_xlim else None

                    with subcols[0]:
                        set_ylim = st.checkbox("ylim",value=False,label_visibility='visible', key='set_ylim_eform')
                    with subcols[1]:
                        ylim = st.slider("ylim", min_value=-20.,max_value=40.,value=(-5.,15.),label_visibility='collapsed', key='ylim_eform')
                    ylim = ylim if set_ylim else None
                    
                with cols[0]:
                    fig1 = da.plot_formation_energies(
                        chemical_potentials=st.session_state.chempots,
                        figsize=figsize,
                        fontsize=fontsize,
                        xlim=xlim,
                        ylim=ylim)
                    fig1.grid()
                    fig1.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                    fig1.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                    st.pyplot(fig1, clear_figure=False, width=fig_width_in_pixels)

#### BROUWER DIAGRAM ####

            if dos and precursors:
                if "brouwer_da" not in st.session_state:
                    st.session_state.brouwer_da = st.session_state.da
                brouwer_da = st.session_state.brouwer_da
                colors = [st.session_state.color_dict[name] for name in brouwer_da.names]
                for color in color_sequence:
                    if color not in colors:
                        colors.append(color)

                cols = st.columns([0.05,0.95])
                with cols[0]:
                    show_brouwer_diagram = st.checkbox("brouwer diagram",value=True,label_visibility='collapsed')
                with cols[1]:
                    st.markdown("<h3 style='font-size:24px;'>Brouwer diagram</h3>", unsafe_allow_html=True)
                if show_brouwer_diagram:
                    cols = st.columns([0.7,0.3])
                    with cols[1]:
                        subcols = st.columns([0.3,0.7])
                        with subcols[0]:
                            set_xlim = st.checkbox("xlim (log)",value=False,label_visibility='visible', key='set_xlim_brouwer')
                        with subcols[1]:
                            default_xlim = int(np.log10(pressure_range[0])) , int(np.log10(pressure_range[1]))
                            xlim = st.slider("xlim (log)", min_value=-50,max_value=30,value=default_xlim,label_visibility='collapsed', key='xlim_brouwer')
                            xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                        xlim = xlim if set_xlim else pressure_range

                        with subcols[0]:
                            set_ylim = st.checkbox("ylim (log)",value=False,label_visibility='visible', key='set_ylim_brouwer')
                        with subcols[1]:
                            ylim = st.slider("ylim (log)", min_value=-50,max_value=30,value=(-20,25),label_visibility='collapsed', key='ylim_brouwer')
                            ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                        ylim = ylim if set_ylim else None

                    with cols[0]:
                        fig2 = brouwer_da.plot_brouwer_diagram(
                            bulk_dos=dos,
                            temperature=temperature,
                            quench_temperature=quench_temperature,
                            quenched_species=quenched_species,
                            quench_elements = quench_elements,
                            precursors=precursors,
                            oxygen_ref=oxygen_ref,
                            pressure_range=pressure_range,
                            external_defects=external_defects,
                            figsize=figsize,
                            fontsize=fontsize,
                            npoints=npoints,
                            xlim=xlim,
                            ylim=ylim,
                            colors=colors,
                        )
                        fig2.grid()
                        fig2.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                        fig2.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                        st.session_state.brouwer_thermodata = brouwer_da.thermodata
                        st.pyplot(fig2, clear_figure=False, width="content")

#### DOPING DIAGRAM ####

            if dos and dopant:
                cols = st.columns([0.05,0.95])
                with cols[0]:
                    show_doping_diagram = st.checkbox("doping diagram",value=True,label_visibility='collapsed')
                with cols[1]:
                    st.markdown("<h3 style='font-size:24px;'>Doping diagram</h3>", unsafe_allow_html=True)
                if show_doping_diagram:
                    cols = st.columns([0.7,0.3])
                    with cols[1]:
                        subcols = st.columns([0.3,0.7])
                        with subcols[0]:
                            set_xlim = st.checkbox("xlim (log)",value=False,label_visibility='visible', key='set_xlim_doping')
                        with subcols[1]:
                            default_xlim = int(np.log10(conc_range[0])) , int(np.log10(conc_range[1]))
                            xlim = st.slider("xlim (log)", min_value=-10,max_value=30,value=default_xlim,label_visibility='collapsed', key='xlim_doping')
                            xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                        xlim = xlim if set_xlim else conc_range

                        with subcols[0]:
                            set_ylim = st.checkbox("ylim (log)",value=False,label_visibility='visible', key='set_ylim_doping')
                        with subcols[1]:
                            ylim = st.slider("ylim (log)", min_value=-50,max_value=30,value=(-20,25),label_visibility='collapsed', key='ylim_doping')
                            ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                        ylim = ylim if set_ylim else None

                    with cols[0]:
                        fig3 = da.plot_doping_diagram(
                            variable_defect_specie=dopant,
                            concentration_range=conc_range,
                            chemical_potentials=st.session_state.chempots,
                            bulk_dos=dos,
                            temperature=temperature,
                            quench_temperature=quench_temperature,
                            quenched_species=quenched_species,
                            figsize=figsize,
                            fontsize=fontsize,
                            npoints=npoints,
                            xlim=xlim,
                            ylim=ylim
                        )
                        fig3.grid()
                        fig3.xlabel(plt.gca().get_xlabel(), fontsize=label_size)
                        fig3.ylabel(plt.gca().get_ylabel(), fontsize=label_size)
                        st.pyplot(fig3, clear_figure=False, width=fig_width_in_pixels)

#### MUE DIAGRAM ####

            if st.session_state.brouwer_thermodata:
                thermodata = st.session_state.brouwer_thermodata
                cols = st.columns([0.05,0.95])
                with cols[0]:
                    show_mue_diagram = st.checkbox("mue diagram",value=True,label_visibility='collapsed')
                with cols[1]:
                    st.markdown("<h3 style='font-size:24px;'>Electron chemical potential</h3>", unsafe_allow_html=True)
                if show_mue_diagram:
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
                    st.pyplot(fig4, clear_figure=False, width=fig_width_in_pixels)

    