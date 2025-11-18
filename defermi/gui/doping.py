
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from defermi.plotter import plot_variable_species_vs_concentrations, plot_variable_species_vs_fermi_level
from defermi.gui.info import cache_info, concentrations_mode_info, dopant_info
from defermi.gui.utils import init_state_variable, download_plot, _get_axis_limits_with_widgets, _filter_concentrations


def settings():
    if st.session_state.da:
        cols = st.columns([0.9,0.1])
        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(dopant_info)

        init_state_variable('dopant_type',value='None')
        init_state_variable('conc_range',value=None)
        init_state_variable('dopant',value={})

        da = st.session_state.da
        possible_dopants = ["None","Donor","Acceptor"]
        for entry in da:
            if entry.defect.type == "Substitution":
                el = entry.defect.specie
                if el not in possible_dopants:
                    possible_dopants.append(el)
        possible_dopants.append('custom')

        # def update_dopant_type_index():
        #     st.session_state['dopant_type'] = st.session_state['widget_select_dopant']
        
        if st.session_state['dopant_type'] in possible_dopants:
            st.session_state['dopant_type_index'] = possible_dopants.index(st.session_state['dopant_type'])
        else:
            st.session_state['dopant_type_index'] = 0
        dopant_type = st.radio("Select dopant",options=possible_dopants,index=st.session_state['dopant_type_index'],
                                        horizontal=True, key='widget_select_dopant')#,on_change=update_dopant_type_index)
        st.session_state['dopant_type'] = dopant_type
        

        dopant_type = st.session_state['dopant_type']    
        if dopant_type == "None":
            st.session_state['dopant'] = None
            st.session_state['conc_range'] = None
            st.session_state.pop('doping_diagram_figure',None)
        elif dopant_type == "Donor":
            cols = st.columns(2)
            with cols[0]:
                d = st.session_state['dopant']
                if d and type(d) == dict and 'charge' in d and d['charge'] > 0: 
                    value = d['charge']
                else:
                    value = 1.0 
                charge = st.number_input("Charge", min_value=0.0, value=value, step = 1.0, key="widget_donor_charge")
            with cols[1]:
                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )
                    return
                if st.session_state['conc_range']:
                    value = int(np.log10(float(st.session_state['conc_range'] [0]))), int(np.log10(float(st.session_state['conc_range'] [1])))
                else:
                    value = (5,18)        
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                                    key="widget_conc_range",on_change=update_conc_range)  
            st.session_state['dopant'] = {"name":"D","charge":charge}
            st.session_state.pop('previous_names_doping',None)

        elif dopant_type == "Acceptor":
            cols = st.columns(2)
            with cols[0]:
                d = st.session_state['dopant']
                if d and type(d) == dict and 'charge' in d and d['charge'] < 0: 
                    value = d['charge']
                else:
                    value = -1.0 
                charge = st.number_input("Charge", max_value=0.0, value=value, step = 1.0, key="widget_acceptor_charge")
            with cols[1]:
                
                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )
                    return
                if st.session_state['conc_range']:
                    value = int(np.log10(float(st.session_state['conc_range'] [0]))), int(np.log10(float(st.session_state['conc_range'] [1])))
                else:
                    value = (5,18)         
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                                    key="widget_conc_range",on_change=update_conc_range) 
            st.session_state['dopant'] = {"name":"A","charge":charge}
            st.session_state.pop('previous_names_doping',None)

        elif dopant_type == "custom":
            cols = st.columns(3)
            d = st.session_state['dopant'] or {}
            with cols[0]:
                value = d['name'] if 'name' in d else 'custom'
                name = st.text_input("Name",value=value, key="widget_name_dopant")          
            with cols[1]:
                if d and type(d) == dict and 'charge' in d:
                    value = d['charge']
                else:
                    value = 0.0
                charge = st.number_input("Charge", value=value, step = 1.0, key="widget_dopant_charge")
            with cols[2]:             
                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )
                    return
                if st.session_state['conc_range']:
                    value = int(np.log10(float(st.session_state['conc_range'] [0]))), int(np.log10(float(st.session_state['conc_range'] [1])))
                else:
                    value = (5,18)         
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                                    key="widget_conc_range",on_change=update_conc_range)
            st.session_state['dopant'] = {"name":name,"charge":charge}
            st.session_state.pop('previous_names_doping',None)

        else:
            cols = st.columns(3)
            with cols[2]:
                st.session_state['dopant'] = dopant_type
                def update_conc_range():
                    min_conc, max_conc = st.session_state['widget_conc_range']
                    st.session_state['conc_range'] = ( float(10**min_conc), float(10**max_conc) )
                    return
                if st.session_state['conc_range']:
                    value = int(np.log10(st.session_state['conc_range'] [0])), int(np.log10(st.session_state['conc_range'] [1]))
                else:
                    value = (5,18)      
                st.slider(r"Range: log₁₀(concentration (cm⁻³))",min_value=-20,max_value=24,value=value,step=1, 
                                        key="widget_conc_range",on_change=update_conc_range)

    
        if st.session_state['dopant']:
            if not st.session_state['conc_range']:
                st.session_state['conc_range'] = (1e05,1e18)

            cols = st.columns([0.3,0.2,0.2,0.3])
            with cols[1]:
                if st.button('Compute',key='widget_clear_cache_doping'):
                    compute_doping_diagram.clear()
            with cols[2]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(cache_info)



@st.cache_data
def compute_doping_diagram():
    st.session_state['da'].plot_doping_diagram(
            variable_defect_specie=st.session_state['dopant'],
            concentration_range=st.session_state['conc_range'],
            chemical_potentials=st.session_state['chempots'],
            bulk_dos=st.session_state['dos'],
            temperature=st.session_state['temperature'],
            quench_temperature=st.session_state['quench_temperature'],
            quenched_species=st.session_state['quenched_species'],
            external_defects=st.session_state['external_defects'],
            npoints=st.session_state['npoints'],
            )
    return st.session_state['da'].thermodata


def get_doping_vs_fermi_level_figure(xlim,ylim=None):
    if st.session_state['doping_thermodata']:    
        figsize = (6,6)
        da = st.session_state['da']
        thermodata = st.session_state['doping_thermodata']

        if type(st.session_state['dopant']) == dict:
            xlabel = st.session_state['dopant']['name']
        else:
            xlabel = st.session_state['dopant']

        fig = plot_variable_species_vs_fermi_level(
                xlabel = xlabel, 
                variable_concentrations=thermodata.variable_concentrations,
                fermi_levels=thermodata.fermi_levels,
                band_gap=da.band_gap,
                figsize=figsize,
                fontsize=st.session_state['fontsize'],
                xlim=xlim,
                ylim=ylim
        )
        fig.grid()
        fig.title('Doping diagram')
        fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
        fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
        ax = fig.gca()
        fig = ax.get_figure()
        fig.patch.set_alpha(st.session_state['alpha'])
        ax.patch.set_alpha(st.session_state['alpha'])
        return fig


def main():

    st.set_page_config(layout="wide")
    st.title("Doping Diagram")
    settings()
    st.divider()

    if "dos" in st.session_state and "dopant" in st.session_state:
        if st.session_state['conc_range']:
            da = st.session_state.da
            conc_range = st.session_state['conc_range']

            cols = st.columns([0.7,0.3])
            with cols[1]:
                default_xlim = int(np.log10(conc_range[0])) , int(np.log10(conc_range[1]))
                set_xlim, xlim = _get_axis_limits_with_widgets(
                                                            label='xlim (log)',
                                                            key='doping',
                                                            default=default_xlim,
                                                            boundaries=default_xlim) 
                xlim = (float(10**xlim[0]) , float(10**xlim[1]))
                xlim = xlim if set_xlim else conc_range

                set_ylim, ylim = _get_axis_limits_with_widgets(
                                                            label='ylim (log)',
                                                            key='doping',
                                                            default=(-20,25),
                                                            boundaries=(-50,30))
                ylim = (float(10**ylim[0]) , float(10**ylim[1]))
                ylim = ylim if set_ylim else None   

                doping_thermodata = compute_doping_diagram()
                dc = doping_thermodata.defect_concentrations[0]
                output, names, charges, colors = _filter_concentrations(dc,key='doping')

            with cols[0]:
                fig = plot_variable_species_vs_concentrations(
                                                doping_thermodata,
                                                output=output,
                                                figsize=st.session_state['figsize'],
                                                fontsize=st.session_state['fontsize'],
                                                colors=colors,
                                                xlim=xlim,
                                                ylim=ylim,
                                                names=names,
                                                charges=charges
                                                )
                fig.grid()
                fig.xlabel(plt.gca().get_xlabel(), fontsize=st.session_state['label_size'])
                fig.ylabel(plt.gca().get_ylabel(), fontsize=st.session_state['label_size'])
                ax = fig.gca()
                fig = ax.get_figure()
                fig.patch.set_alpha(st.session_state['alpha'])
                ax.patch.set_alpha(st.session_state['alpha'])
                st.session_state['doping_thermodata'] = doping_thermodata
                st.session_state['doping_diagram_figure'] = fig
                st.pyplot(fig, clear_figure=False, width="stretch")

                fig = get_doping_vs_fermi_level_figure(xlim,ylim=None)
                st.session_state['fermi_level_doping_figure'] = fig 

            with cols[1]:
                with st.popover(label='ℹ️',help='Info',type='tertiary'):
                    st.write(concentrations_mode_info)
                st.write('')
                download_plot(fig=fig,filename='doping_diagram.pdf')


if __name__ == '__main__':
    main()