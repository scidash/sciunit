.. sciunit documentation master file, created by
   sphinx-quickstart on Thu Feb 13 13:47:10 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to sciunit's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. figure:: https://raw.githubusercontent.com/scidash/assets/master/logos/SciUnit/sci-unit-square-small.png
    :align: center
    
=======================================================================================

Concept
-------

`The conference
paper <https://github.com/cyrus-/papers/raw/master/sciunit-icse14/sciunit-icse14.pdf>`__

Tutorials With Jupyter NoteBook 
-------------------------------

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/scidash/sciunit/blob/master/docs/chapter1.ipynb

* `Tutorial Chapter 1`_
* `Tutorial Chapter 2`_
* `Tutorial Chapter 3`_
* `Tutorial Chapter 4`_
* `Tutorial Chapter 5`_
* `Tutorial Chapter 6`_

.. _Tutorial Chapter 1: https://github.com/scidash/sciunit/blob/master/docs/chapter1.ipynb
.. _Tutorial Chapter 2: https://github.com/scidash/sciunit/blob/master/docs/chapter2.ipynb
.. _Tutorial Chapter 3: https://github.com/scidash/sciunit/blob/master/docs/chapter3.ipynb
.. _Tutorial Chapter 4: https://github.com/scidash/sciunit/blob/dev/docs/chapter4.ipynb
.. _Tutorial Chapter 5: https://github.com/scidash/sciunit/blob/dev/docs/chapter5.ipynb
.. _Tutorial Chapter 6: https://github.com/scidash/sciunit/blob/dev/docs/chapter6.ipynb

Basic Usage
-----------

.. code:: python

    my_model = MyModel(**my_args) # Instantiate a class that wraps your model of interest.  
    my_test = MyTest(**my_params) # Instantiate a test that you write.  
    score = my_test.judge() # Runs the test and return a rich score containing test results and more.  

Domain-specific libraries and information
-----------------------------------------

`NeuronUnit <https://github.com/scidash/neuronunit>`__ for neuron and
ion channel physiology See others
`here <https://github.com/scidash/sciunit/network/dependents?dependent_type=REPOSITORY>`__

Mailing List
------------

There is a `mailing
list <https://groups.google.com/forum/?fromgroups#!forum/sciunit>`__ for
announcements and discussion. Please join it if you are at all
interested!

Contributors
------------

-  `Rick Gerkin <http://rick.gerk.in>`__, Arizona State University
   (School of Life Science)
-  `Cyrus Omar <http://cs.cmu.edu/~comar>`__, Carnegie Mellon University
   (Dept. of Computer Science)

Reproducible Research ID
------------------------

RRID:\ `SCR\_014528 <https://scicrunch.org/resources/Any/record/nlx_144509-1/3faed1d9-6579-5da6-b4b4-75a5077656bb/search?q=sciunit&l=sciunit>`__

License
-------

SciUnit is released under the permissive `MIT
license <https://opensource.org/licenses/MIT>`__, requiring only
attribution in derivative works. See the LICENSE file for terms.


Table of Contents
-----------------

.. toctree::

   setup
   quick_tutorial
   basics
   commandline

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
