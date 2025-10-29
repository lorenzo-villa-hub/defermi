
import os

import defermi

def setup_gui(subparsers):

    subparsers_gui = subparsers.add_argument('gui',help='Launch GUI with streamlit',default=False,action='store_true',dest='gui')
    subparsers_gui.set_defaults(func=run_gui)


def run_gui(args):
    path_defermi = defermi.__file__
    path_gui_main = path_defermi.replace('__init__.py','gui/main.py')
    os.system(f'streamlit run {path_gui_main}')

    

