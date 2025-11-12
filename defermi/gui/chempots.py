
import streamlit as st

from pymatgen.core.composition import Composition

from defermi.chempots.generator import generate_elemental_chempots, generate_chempots_from_condition
from defermi.gui.info import chempots_info
from defermi.gui.utils import init_state_variable, widget_with_updating_state, reset_home_figures

def chempots():
    """
    GUI elements for chemical potentials 
    """
    if st.session_state.da:
        da = st.session_state.da
        init_state_variable('chempots',value={})
        chempots_DB = {}

        def set_chempots_from_DB(composition,condition):
            if composition:
                chempots_DB = pull_chempots_from_condition(
                                                        composition=composition,
                                                        condition=condition)
                elements_in_composition = [el.symbol for el in composition.elements]
                elements_to_pull = [el for el in da.elements if el not in elements_in_composition]
                chempots_elemental = pull_elemental_chempots_from_MP(elements_to_pull)
                for el,mu in chempots_elemental.items():
                    chempots_DB[el] = mu
            else:
                chempots_DB = pull_elemental_chempots_from_MP(da.elements)
            
            for el,mu in chempots_DB.items():
                st.session_state[f'widget_chempot{el}'] = mu
            reset_home_figures()
            return
        

        cols = st.columns([0.36,0.55,0.09])
        with cols[0]:
            st.markdown("**Chemical Potentials (eV)**")
        with cols[1]:
            with st.expander('🗄️ Materials Project Database'):
                help = ""
                composition = st.text_input('Reference composition',
                                                    value='',
                                                    placeholder='Empty for elemental chemical potentials',
                                                    help = 'Composition of the pristine material',
                                                    key='widget_composition_DB')
                if composition:
                    composition = Composition(composition)
                    subcols = st.columns(2)
                    with subcols[0]:
                        options = [el.symbol for el in composition.elements]
                        if 'O' in options:
                            index = options.index('O')
                        element = st.radio(label='Element',options=options,index=index)
                    with subcols[1]:
                        condition_str = st.radio(label='Condition',options=['middle','rich','poor'],index=0)
                    condition = '-'.join([element,condition_str])
                else:
                    condition = None
                st.button('Pull',on_click=set_chempots_from_DB,args=[composition,condition])
                    
        with cols[2]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(chempots_info)

        mu_string = "μ"
        
        ncolumns = 4
        cols = st.columns(ncolumns)
        for idx,el in enumerate(da.elements):
            col_idx = idx%ncolumns
            with cols[col_idx]:
                if el in st.session_state['chempots']:
                    widget_key = f'widget_chempot{el}'
                    if widget_key not in st.session_state:
                        st.session_state[widget_key] = st.session_state['chempots'][el] or 0.0

                mu = st.number_input(f"{mu_string}({el})", max_value=0.0,step=0.5, key=f'widget_chempot{el}',on_change=reset_home_figures)
                st.session_state.chempots[el] = mu

        st.divider()



def pull_elemental_chempots_from_MP(elements,thermo_type='GGA_GGA+U',**kwargs):
    """
    Generate chemical potentials for reference elemental phases from the
    Materials Project database.

    Parameters
    ----------
    elements : list
        List of strings with element symbols.
    thermo_type : str
        The thermo type to pass to MP database. 
    kwargs : dict
        Kwargs to pass to `get_phase_diagram_from_chemsys`.

    Returns
    -------
    Chempots object
    """
    import base64
    from defermi.tools.materials_project import MPDatabase

    API_KEY = base64.b64decode('Q0FVMk8yODZmRUI2cGJWOUszTU9qblFFUFJkZW9BQXg=').decode()
    chempots = generate_elemental_chempots(
                                        elements,
                                        API_KEY=API_KEY,
                                        thermo_type=thermo_type,
                                        **kwargs)
    return chempots


def pull_chempots_from_condition(composition,condition,thermo_type='GGA_GGA+U',**kwargs):

    import base64
    from defermi.tools.materials_project import MPDatabase

    API_KEY = base64.b64decode('Q0FVMk8yODZmRUI2cGJWOUszTU9qblFFUFJkZW9BQXg=').decode()
    chempots = generate_chempots_from_condition(
                                            composition=composition,
                                            condition=condition,
                                            API_KEY=API_KEY,
                                            thermo_type=thermo_type,
                                            **kwargs)
    return chempots


