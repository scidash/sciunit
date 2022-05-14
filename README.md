[![Python package](https://github.com/scidash/sciunit/actions/workflows/python-package.yml/badge.svg)](https://github.com/scidash/sciunit/actions/workflows/python-package.yml)
[![RTFD](https://readthedocs.org/projects/sciunit/badge/?version=master&x=1)](http://sciunit.readthedocs.io/en/latest/?badge=master)
[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/scidash/sciunit/master?filepath=docs%2Fchapter1.ipynb)
[![Coveralls](https://coveralls.io/repos/github/scidash/sciunit/badge.svg?branch=master&x=1)](https://coveralls.io/github/scidash/sciunit?branch=master)
[![Repos using Sciunit](https://img.shields.io/librariesio/dependent-repos/pypi/sciunit.svg?x=3)](https://github.com/scidash/sciunit/network/dependents?dependent_type=REPOSITORY)
![Downloads from PyPI](https://img.shields.io/pypi/dm/sciunit?x=1)

<img src="https://raw.githubusercontent.com/scidash/assets/master/logos/SciUnit/sci-unit-square-small.png" alt="SciUnit Logo" width="400px">

# SciUnit: A Test-Driven Framework for Formally Validating Scientific Models Against Data

## Concept
[The conference paper](https://github.com/cyrus-/papers/raw/master/sciunit-icse14/sciunit-icse14.pdf)

## Documentation
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scidash/sciunit/blob/master/docs/chapter1.ipynb) <br>
[Jupyter Tutorials](https://scidash.org/sciunit/README.html)<br>
[API Documentation](http://sciunit.rtfd.io)

## Installation
```python
pip install sciunit
```
or
```python
conda install -c conda-forge sciunit
```

## Basic Usage
```python
my_model = MyModel(**my_args) # Instantiate a class that wraps your model of interest.  
my_test = MyTest(**my_params) # Instantiate a test that you write.  
score = my_test.judge() # Runs the test and return a rich score containing test results and more.  
```

## Domain-specific libraries and information
[NeuronUnit](https://github.com/scidash/neuronunit) for neuron and ion channel physiology<br>
See others [here](https://github.com/scidash/sciunit/network/dependents?dependent_type=REPOSITORY)

## Mailing List
There is a [mailing list](https://groups.google.com/forum/?fromgroups#!forum/sciunit) for announcements and discussion.
Please join it if you are at all interested!

## Contributors
 * [Rick Gerkin](http://rick.gerk.in), Arizona State University (School of Life Science)
 * [Cyrus Omar](http://cs.cmu.edu/~comar), Carnegie Mellon University (Dept. of Computer Science)

## Reproducible Research ID
RRID:[SCR_014528](https://scicrunch.org/resources/Any/record/nlx_144509-1/3faed1d9-6579-5da6-b4b4-75a5077656bb/search?q=sciunit&l=sciunit)

## License
SciUnit is released under the permissive [MIT license](https://opensource.org/licenses/MIT), requiring only attribution in derivative works. See the LICENSE file for terms.
