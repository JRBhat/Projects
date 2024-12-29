"""
Configuration file for the Sphinx documentation builder.

This file contains the most common configurations.
For more options, see:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath('.'))
sys.path.append('source')

# -- Project information -----------------------------------------------------
project: str = "DocToLatex Conversion Tool - Information for Developers"
copyright: str = '2020, JB'
author: str = 'Jayesh Bhat'
release: str = '1.0'  # Full version, including alpha/beta/rc tags

# -- General configuration ---------------------------------------------------
extensions: list[str] = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

exclude_patterns: list[str] = ['build']  # Files/directories to ignore
add_module_names: bool = False  # Do not prepend module names to unit titles
pygments_style: str = 'sphinx'  # Syntax highlighting style

# -- Options for HTML output -------------------------------------------------
html_theme: str = 'alabaster'
html_static_path: list[str] = ['_static']

# -- Options for LaTeX output ------------------------------------------------
latex_preamble: str = """
\\newcommand{\\leadingzero}[1]{\\ifnum #1<10 0\\the#1\\else\\the#1\\fi}
\\newcommand{\\HRule}{\\rule{\\linewidth}{0.5mm}}
\\definecolor{Black}{rgb}{0.0,0.0,0.0}
\\definecolor{LightBlue}{rgb}{0.718,0.78,0.91}
\\definecolor{DarkBlue}{rgb}{0.212,0.416,0.706}
\\usepackage{url}
"""

latex_elements: dict[str, str] = {
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'classoptions': ',oneside',
    'preamble': latex_preamble
}

latex_logo: str = 'proderm-logo.png'
latex_domain_indices: bool = False  # Do not generate module index
