.. _gui_manual:
.. index:: User Interface

Defermi UI - User manual
========================

.. image:: https://static.streamlit.io/badges/streamlit_badge_black_white.svg
   :target: https://defermi.streamlit.app/

.. image:: https://img.shields.io/badge/github-repo-blue?logo=github
   :target: https://github.com/lorenzo-villa-hub/defermi-gui

.. image:: https://img.shields.io/pypi/v/defermi-gui
   :target: https://pypi.org/project/defermi-gui/

|

.. image:: ./images/main.png
   :width: 70%
   :align: center

``defermi`` comes with a User Interface (UI). The main workflows from the Python library are available.

Index
-----

- `Running the app`_
- `Getting started`_
- `Sidebar`_
- `Pages`_

Running the app
---------------

Online
~~~~~~~~

The ``defermi`` app can be run online (no installation) at this link: `https://defermi.streamlit.app/ <https://defermi.streamlit.app/>`_

Locally
~~~~~~~

The app can also be run locally offline. Install it with ``pip``:

.. code-block:: bash

    pip install defermi-gui

Launch the app by running this in the terminal:

.. code-block:: bash

    defermi-gui

Getting started
---------------

The philosophy of point-defects thermodynamics is to collectively analyse a collection 
of individual defect calculations. The app loads data relative to this collection of defects.
Load a preset from the `Home`_ page to get started. 

.. image:: ./images/home/presets.png
   :width: 50%
   :align: center


Click on `Data`_ to view the raw dataset. Every cell can be modified (like an Excel table).

.. image:: ./images/data/data.png
   :width: 50%
   :align: center

Modify chemical potentials in the `Sidebar`_ or pull them from the `Materials Project <https://next-gen.materialsproject.org/>`_ database. 



.. list-table::
   :width: 100%
   :class: borderless

   * - .. image:: ./images/sidebar/chempots.png
          :width: 100%
         
     - .. image:: ./images/sidebar/chempots_MP_elemental.png
          :width: 100%


View formation energy vs Fermi level plots by clicking on the `Formation energies`_ page. 

|

.. image:: ./images/formation-energies/formation_energies.png
   :width: 70%
   :align: center


Sidebar
=======

The top half of the sidebar contains the page navigation menu (more details in the `Pages`_ section),
the bottom half contains parameters that are common for different pages. 

.. image:: ./images/sidebar/sidebar_main_top_bottom.png
   :width: 50%
   :align: center

Once a dataset (or a preset) is loaded, the following parameters will appear in the bottom half of the sidebar:

.. image:: ./images/sidebar/sidebar_main_bottom.png
   :width: 40%
   :align: center

1) `File uploader`_ 
2) `Chemical potentials`_
3) `Density of states`_
4) `Temperature`_
5) `External defects`_

File uploader
-------------

Chemical potentials
-------------------

Density of states
-----------------

Temperature
-----------

External defects
----------------


Pages
=====

- `Home`_
- `Overview`_
- `Data`_
- `Formation energies`_
- `Doping`_
- `Brouwer`_
- `Fermi level`_
- `Charge transition levels`_
- `Binding energies`_

Home
----

Overview
--------

Data
----

Formation energies
------------------

Doping
------

Brouwer
-------

Fermi level
-----------

Charge transition levels
------------------------

Binding energies
----------------
