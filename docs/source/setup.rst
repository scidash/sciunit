What's SciUnit and how to install it?
=====================================

Everyone hopes that their model has some correspondence with reality. 
Usually, checking whether this is true is done informally. But SciUnit makes this formal and transparent.

SciUnit is a framework for validating scientific models by creating experimental-data-driven unit tests.

Installation
----------------

Note: SciUnit no longer supports Python 2. Please use Python 3.

SciUnit can be installed in virtual environments using the :code:`pip` Python package installer.
A virtual environment can be set up using the in-built Python :code:`venv` module, as explained `here <https://docs.python.org/3/tutorial/venv.html>`__, or using other tools such as `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__.


In the virtual environment, run the following command to install SciUnit as a Python package using :code:`pip`.

.. code-block:: bash

    pip install sciunit


On `Fedora Linux <https://getfedora.org>`__ installations, the `NeuroFedora special interest group <https://neuro.fedoraproject.org>`__ also provides SciUnit as a curated package in the Fedora community repositories.
SciUnit can, therefore, be installed using the system package manager, :code:`dnf` :

.. code-block:: bash

    sudo dnf install python3-sciunit
