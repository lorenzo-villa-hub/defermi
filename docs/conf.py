# # Configuration file for the Sphinx documentation builder.
# #
# # For the full list of built-in configuration values, see the documentation:
# # https://www.sphinx-doc.org/en/master/usage/configuration.html

# # -- Project information -----------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# project = 'defy'
# copyright = '2025, Lorenzo Villa'
# author = 'Lorenzo Villa'
# release = '1.0.0'

# # -- General configuration ---------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = []

# templates_path = ['_templates']
# exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# # -- Options for HTML output -------------------------------------------------
# # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
# html_static_path = ['_static']

# docs/conf.py

import os
import sys

# Make sure your package is importable
# If your package is in the top-level folder "defy", use:
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = "defy"
author = "Lorenzo Villa"
release = "1.0.0"  # or import from your package, e.g. defy.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",            # support Google / NumPy style docstrings
    "sphinx_autodoc_typehints",       # show type hints
    "myst_parser",                    # support Markdown
    "sphinx.ext.viewcode",            # add “view source” links
    # "nbsphinx",                      # (optional) support Jupyter notebooks
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# If you want to support both .rst and .md
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
# If you want your index to be index.md, set this to "index"
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_logo = None  # or path to a logo file

# -- Autodoc / napoleon settings ----------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# If you want to automatically generate module pages from your package:
# (you can also use sphinx-apidoc externally)

