# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import wayfarer  # noqa: F401

project = "Wayfarer"
copyright = "2023, Compass Informatics"
author = "Seth Girvin"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_material"

html_show_sourcelink = False

html_static_path = ["_static"]

html_title = "Wayfarer"

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = []

# html_theme_options = {
#   "sidebar_secondary": {"remove": "true"}
# }

# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/configuring.html?highlight=html_sidebars#remove-the-sidebar-from-some-pages

# html_sidebars = {
#    "**": []
# }

html_js_files = []

napoleon_use_param = True
