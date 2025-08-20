# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import wayfarer  # noqa: F401

project = "Wayfarer"
copyright = "2025, Compass Informatics"
author = "Seth Girvin"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "networkx": ("https://networkx.org/documentation/stable/", None),
    "shapely": ("https://shapely.readthedocs.io/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# added the following to avoid WARNING: cannot cache unpickable configuration value: 'html_context'
# in the sphinx_material theme
suppress_warnings = ["config.cache"]

html_theme = "sphinx_material"

html_show_sourcelink = False

html_static_path = ["_static"]

html_title = "Wayfarer"

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = []

html_theme_options = {
    "nav_title": "Wayfarer",
    "globaltoc_depth": 2,
    "globaltoc_collapse": True,
    "globaltoc_includehidden": True,
}

html_sidebars = {"**": ["globaltoc.html", "localtoc.html", "searchbox.html"]}

html_js_files = []

napoleon_use_param = True
