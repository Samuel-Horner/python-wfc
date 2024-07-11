.. python-wfc documentation master file, created by
   sphinx-quickstart on Thu Jul 11 12:02:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-wfc's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
======================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


**python-wfc**
This is a python library implementing the core of the wave function collapse algorithm.

wfc.core
=====================================

.. automodule:: wfc.core

**classes**

.. autoexception:: TileSetError
.. autoclass:: Pos
   :members:
.. autoclass:: Tile
   :members:
.. autoclass:: Cell
.. autoclass:: Map
   :members:

**functions**

.. autofunction:: generate_tileset
.. autofunction:: parse_input

wfc.examples.cli
======================================

.. module:: wfc.examples.cli

**functions**

.. autofunction:: main
.. autofunction:: animate_map
.. autofunction:: print_map
.. autofunction:: parse_file
