"""Sphinx configuration for the ADAMSNRC documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "ADAMSNRC"
author = "Max Oliver, CTO 3Flux.com"
copyright = "2025, Max Oliver"  # noqa: A001
release = "2.0.14"
version = release

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_title = "ADAMSNRC API Client"
html_static_path = []
templates_path = []

autodoc_member_order = "bysource"
autodoc_typehints = "description"
