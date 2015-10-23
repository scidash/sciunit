[![Build Status](https://travis-ci.org/rgerkin/sciunit.svg?branch=master)](https://travis-ci.org/rgerkin/sciunit)

![SciUnit Logo](https://raw.githubusercontent.com/scidash/assets/master/logos/sciunit.png)
# SciUnit: A Test-Driven Framework for Formally Validating Scientific Models Against Data

## Concept
[The conference paper](https://github.com/cyrus-/papers/raw/master/sciunit-icse14/sciunit-icse14.pdf)

## Documentation
[Chapter 1](https://github.com/scidash/sciunit/blob/master/docs/chapter1.ipynb) / 
[Chapter 2](https://github.com/scidash/sciunit/blob/master/docs/chapter2.ipynb) /
[Chapter 3](https://github.com/scidash/sciunit/blob/master/docs/chapter3.ipynb) /

## Basic Usage
```python
my_model = MyModel(**my_args) # Instantiate a class that wraps your model of interest.  
my_test = MyTest(**my_params) # Instantiate a test that you write.  
score = my_test.judge() # Runs the test and return a rich score containing test results and more.  
```

## Domain-specific libraries and information

[NeuronUnit](https://github.com/scidash/neuronunit) for neuron and ion channel physiology

## Mailing List
There is a [mailing list](https://groups.google.com/forum/?fromgroups#!forum/sciunit) for announcements and discussion.
Please join it if you are at all interested!

## Contributors
 * [Cyrus Omar](http://cs.cmu.edu/~comar), Carnegie Mellon University (Dept. of Computer Science)
 * [Rick Gerkin](http://rick.gerk.in), Arizona State University (School of Life Science)

## License
SciUnit is released under the permissive [MIT license](https://opensource.org/licenses/MIT), requiring only attribution in derivative works. See the LICENSE file for terms.
