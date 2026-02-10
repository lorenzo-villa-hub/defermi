import os
import sys
from datetime import date

# -- Path setup --------------------------------------------------------------
# Insert project root so Sphinx can find your code
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = "Defermi"
copyright = f"{date.today().year}, Lorenzo Villa"
author = "Lorenzo Villa"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",       # Core library for generating docs from docstrings
    "sphinx.ext.autosummary",  # The engine for the summary tables (abTEM style)
    "sphinx.ext.napoleon",     # Support for Google/NumPy style docstrings
    "sphinx.ext.viewcode",     # Add links to highlighted source code
    "nbsphinx",                # Jupyter Notebook support
    "myst_parser",             # Markdown support
]

# Autosummary settings:
# This ensures that Sphinx automatically creates the stub files for your API
autosummary_generate = True  
autosummary_imported_members = False

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,   # Shows "Bases: numpy.ndarray" text
    'inherited-members': False,  # THIS IS THE KEY: it won't pull in methods from parent classes
}

# General Sphinx settings
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# -- Autodoc & API options ---------------------------------------------------
autoclass_content = "both"     # Include both class and __init__ docstrings
add_module_names = False       # Prevents 'defermi.plotter' and shows just 'plotter'
autodoc_inherit_docstrings = True
set_type_hints = "none"        # Makes signatures much cleaner (like abTEM)

# -- Notebook & Markdown options ---------------------------------------------
nb_execution_mode = "off"
myst_enable_extensions = ["attrs_inline"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_static_path = ['_static']
html_theme = 'sphinx_book_theme'
