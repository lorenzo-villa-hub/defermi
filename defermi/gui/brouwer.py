
import numpy as np
import uuid
import streamlit as st
import matplotlib.pyplot as plt

from pymatgen.core.composition import Composition

from defermi.plotter import plot_pO2_vs_concentrations, plot_pO2_vs_fermi_level
from defermi.gui.info import precursors_info, oxygen_ref_info, cache_info, concentrations_mode_info, brouwer_diagram_info
from defermi.gui.utils import init_state_variable, download_plot, _get_axis_limits_with_widgets, _filter_concentrations


def oxygen_ref():
    init_state_variable('oxygen_ref',value=-4.95)
    subcols = st.columns([0.2,0.8])
    with subcols[0]:
        oxygen_ref = st.number_input('**μO (0K, p0) [eV]**', value=st.session_state['oxygen_ref'], step=0.5, key='widget_oxygen_ref',label_visibility='visible')
        st.session_state['oxygen_ref'] = oxygen_ref
    with subcols[1]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(oxygen_ref_info)


def precursors():
    if st.session_state.da:
        da = st.session_state.da
        cols = st.columns([0.9,0.1])
        with cols[0]:
            st.markdown("##### Precursors")
        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(precursors_info)

        init_state_variable('precursor_entries',value=[]) 
        
        cols = st.columns([0.1, 0.25, 0.25, 0.3, 0.1])
        with cols[0]:
            add_precursors = st.button("➕",key="widget_add_precursor")
            if add_precursors:
                # Generate a unique ID for this entry
                entry_id = str(uuid.uuid4())
                st.session_state.precursor_entries.append({
                    "id": entry_id,
                    "composition": "",
                    "energy": 0.0
                })

        def remove_precursor_entry(entry_id):
            for idx,entry in enumerate(st.session_state['precursor_entries']):
                if entry['id'] == entry_id:
                    del st.session_state['precursor_entries'][idx]

        init_state_variable('precursor_DB_warning',value=None)
        def set_precursor_energy_from_DB(entry):
            if entry['composition']:
                energy_pfu = pull_stable_energy_pfu_from_composition(composition=entry['composition'])
                st.session_state[f"widget_energy_{entry['id']}"] = energy_pfu
            else:
                st.session_state['precursor_DB_warning'] = 'Enter composition to pull energy from MP database'
            return 


        for entry in st.session_state['precursor_entries']:
            with cols[1]:
                entry["composition"] = st.text_input("Composition", value=entry["composition"], key=f"widget_comp_{entry['id']}")
            with cols[2]:
                widget_key = f"widget_energy_{entry['id']}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = entry['energy']
                energy = st.number_input("Energy p.f.u (eV)", step=1.0, key=f"widget_energy_{entry['id']}")
                entry["energy"] = energy
            with cols[3]:
                st.write('')
                st.button('🗄️ Materials Project DB',on_click=set_precursor_energy_from_DB,args=[entry],key=f"widget_pull_{entry['id']}")
            if st.session_state['precursor_DB_warning']:
                st.error(st.session_state['precursor_DB_warning'])
                st.session_state['precursor_DB_warning'] = None
            with cols[4]:
                st.write('')
                st.button("🗑️", on_click=remove_precursor_entry, args=[entry['id']], key=f"widget_del_{entry['id']}")

        st.session_state['precursors'] = {
                            entry["composition"]: entry["energy"] 
                            for entry in st.session_state.precursor_entries
                            if entry["composition"]}



def filter_entries_with_missing_elements():
    """
    Remove defect entries with elements missing from precursors from brouwer diagram dataset.
    """
    if "precursors" in st.session_state and st.session_state.da:
        precursors = st.session_state['precursors']
        da = st.session_state.da
        # remove defect entries with missing precursors from brouwer diagram dataset
        elements_in_precursors = set()
        if precursors:
            for comp in precursors:
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
            try:
                brouwer_da = da.filter_entries(elements=filter_elements)
            except AttributeError:
                st.warning('No entries for Brouwer diagram calculation')
                brouwer_da = None
        else:
            brouwer_da = None       
        
        st.session_state['brouwer_da'] = brouwer_da
        st.session_state['quenched_species_brouwer'] = []
        if brouwer_da:
            if st.session_state['quenched_species']:
                if st.session_state['quench_elements']:
                    for entry in brouwer_da.entries:
                        for df in entry.defect:
                            if df.type == 'Vacancy':
                                if df.name in st.session_state['quenched_species']:
                                    st.session_state['quenched_species_brouwer'].append(df.name)
                            else:
                                if df.specie in st.session_state['quenched_species']:
                                    st.session_state['quenched_species_brouwer'].append(df.specie)

                else:
                    for species in st.session_state['quenched_species']:
                        if species in brouwer_da.names:
                            st.session_state['quenched_species_brouwer'].append(species)
    else:
        st.session_state.pop('brouwer_diagram_figure',None)
        st.session_state.pop('fermi_level_brouwer_figure',None)
        



def pull_stable_energy_pfu_from_composition(composition,thermo_types=['GGA_GGA+U'],**kwargs):
    import base64
    from defermi.tools.materials_project import MPDatabase

    API_KEY = base64.b64decode('Q0FVMk8yODZmRUI2cGJWOUszTU9qblFFUFJkZW9BQXg=').decode()
    energy_pfu = MPDatabase(API_KEY=API_KEY).get_stable_energy_pfu_from_composition(
                                                                                composition=composition,
                                                                                thermo_types=thermo_types,
                                                                                **kwargs)
    return energy_pfu


@st.cache_data
def compute_brouwer_diagram(_brouwer_da):
    _brouwer_da.plot_brouwer_diagram(
                            bulk_dos=st.session_state['dos'],
                            temperature=st.session_state['temperature'],
                            quench_temperature=st.session_state['quench_temperature'],
                            quenched_species=st.session_state['quenched_species_brouwer'],
                            quench_elements = st.session_state['quench_elements'],
                            precursors=st.session_state['precursors'],
                            oxygen_ref=st.session_state['oxygen_ref'],
                            pressure_range=st.session_state['pressure_range'],
                            external_defects=st.session_state['external_defects'],
                            npoints=st.session_state['npoints']
                        )
    return _brouwer_da.thermodata


def get_pO2_vs_fermi_level_figure(xlim,ylim):
    if st.session_state['brouwer_thermodata']:    
        figsize = (6,6)
        da = st.session_state.da
        thermodata = st.session_state.brouwer_thermodata

        fig = plot_pO2_vs_fermi_level(
                partial_pressures=thermodata.partial_pressures,
                fermi_levels=thermodata.fermi_levels,
                band_gap=da.band_gap,
                figsize=figsize,
                fontsize=st.session_state['fontsize'],
                xlim=xlim,
                ylim=ylim
        )
        fig.grid()
        fig.title('Brouwer diagram')
        fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
        fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
        ax = fig.gca()
        fig = ax.get_figure()
        fig.patch.set_alpha(st.session_state['alpha'])
        ax.patch.set_alpha(st.session_state['alpha'])
        return fig



def main():

    st.set_page_config(layout="wide")
    cols = st.columns([0.4,0.6])
    with cols[0]:
        st.title('Brouwer Diagram')
    with cols[1]:
        with st.popover(label='ℹ️',help='Info',type='tertiary'):
            st.write(brouwer_diagram_info)
    if st.session_state.da and 'O' in st.session_state.da.elements:
        st.write('')
        oxygen_ref()
        precursors()
        filter_entries_with_missing_elements()

        cols = st.columns([0.3,0.2,0.2,0.3])
        with cols[1]:
            if st.button('Compute',key='widget_clear_cache_brouwer'):
                compute_brouwer_diagram.clear()
        with cols[2]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(cache_info)

        st.divider()


        if "dos" in st.session_state and "precursors" in st.session_state:
            if st.session_state['precursors']:
                pressure_range = st.session_state['pressure_range']
                brouwer_da = st.session_state['brouwer_da'] 
                if brouwer_da:
                    cols = st.columns([0.7,0.3])
                    with cols[1]:
                        default_xlim = int(np.log10(pressure_range[0])) , int(np.log10(pressure_range[1]))
                        set_xlim, xlim = _get_axis_limits_with_widgets(
                                                                    label='xlim (log)',
                                                                    key='brouwer',
                                                                    default=default_xlim,
                                                                    boundaries=default_xlim) 
                        xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                        xlim = xlim if set_xlim else pressure_range

                        set_ylim, ylim = _get_axis_limits_with_widgets(
                                                                    label='ylim (log)',
                                                                    key='brouwer',
                                                                    default=(-20,25),
                                                                    boundaries=(-50,30))
                        ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                        ylim = ylim if set_ylim else None   

                        brouwer_thermodata = compute_brouwer_diagram(_brouwer_da=brouwer_da) # leading underscore tells streamlit not to hash the argument
                        dc = brouwer_thermodata.defect_concentrations[0]
                        output, names, charges, colors = _filter_concentrations(dc,key='brouwer')

                    with cols[0]:  
                        fig = plot_pO2_vs_concentrations(
                                                    thermodata=brouwer_thermodata,
                                                    output=output,
                                                    figsize=st.session_state['figsize'],
                                                    fontsize=st.session_state['fontsize'],
                                                    xlim=xlim,
                                                    ylim=ylim,
                                                    colors=colors,
                                                    names=names,
                                                    charges=charges)                                           

                        fig.grid()
                        fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
                        fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
                        ax = fig.gca()
                        fig = ax.get_figure()
                        fig.patch.set_alpha(st.session_state['alpha'])
                        ax.patch.set_alpha(st.session_state['alpha'])
                        st.session_state['brouwer_thermodata'] = brouwer_thermodata
                        st.session_state['brouwer_diagram_figure'] = fig
                        st.pyplot(fig, clear_figure=False, width="stretch")

                        fig = get_pO2_vs_fermi_level_figure(xlim,ylim)
                        st.session_state['fermi_level_brouwer_figure'] = fig

                    with cols[1]:
                        with st.popover(label='ℹ️',help='Info',type='tertiary'):
                            st.write(concentrations_mode_info)
                        st.write('')
                        download_plot(fig=fig,filename='brouwer_diagram.pdf')

    elif st.session_state.da and 'O' not in st.session_state.da.elements:
        st.warning('Brouwer analysis concerns only systems containing Oxygen')


if __name__ == '__main__':
    main()