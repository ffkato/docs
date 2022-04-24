# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'Functional Kato Docs'
copyright = 'ffkato'
author = 'ffkato'

release = ''
version = ''

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx_markdown_tables',
]

source_suffix = ['.rst', '.md']

source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}

master_doc = 'index'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

html_css_files = [
    'style.css',
]
