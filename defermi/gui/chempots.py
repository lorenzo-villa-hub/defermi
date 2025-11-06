
import streamlit as st

from defermi.gui.utils import init_state_variable

def chempots():
    """
    GUI elements for chemical potentials 
    """
    if st.session_state.da:
        da = st.session_state.da

        cols = st.columns([0.9,0.1])
        with cols[0]:
            st.markdown("**Chemical Potentials (eV)**")
        with cols[1]:
            with st.popover(label='ℹ️',help='Info',type='tertiary'):
                st.write(chempots_info)

        mu_string = "μ"
        init_state_variable('chempots',value={})

        cols = st.columns(5)
        for idx,el in enumerate(da.elements):
            ncolumns = 5
            col_idx = idx%ncolumns
            with cols[col_idx]:
                value = st.session_state['chempots'][el] if el in st.session_state['chempots'] else 0.0
                st.session_state.chempots[el] = st.number_input(f"{mu_string}({el})", value=value, max_value=0.0,step=0.5, key=f'widget_chempot{el}')



def pull_elemental_chempot_from_MP(element):
    import base64
    from defermi.tools.materials_project import MPDatabase

    API_KEY = base64.b64decode('Q0FVMk8yODZmRUI2cGJWOUszTU9qblFFUFJkZW9BQXg=').decode()
    mpdb = MPDatabase(API_KEY=API_KEY)
    return mpdb.get_stable_energy_pfu_from_composition('Na')


chempots_info = """
Chemical potential of the elements that are exchanged with a reservoirs when defects are formed.\n

Formation energies depend on the chemical potentials as:\n
$$ \Delta E_f = E_D - E_B + q(\epsilon_{VBM} + \epsilon_F) - \color{blue} \sum_i \Delta n_i \mu_i $$ \n

where $\Delta n_i$ is the number of particles in the defective cell minus the number in the pristine cell for species $i$.
"""