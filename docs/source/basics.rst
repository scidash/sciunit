SciUnit basics
==============

This page will give you a basic view of the SciUnit project, 
and you can read the quick tutorials for some simple examples.

The major parts of SciUnit are Score, Test, and Model. 

Model
------

``Model`` is the abstract base class for sciunit models. Generally, a model instance can
generate predicted or simulated results of some scientific fact.


Runnable Model

``Runnable model`` is a kind of model that implements Runnable 
capability, and it can be executed to simulate and output results.


Backend

After being registered by ``register_backends`` function, a ``Backend`` instance
can be executed by a Ruunable Model at the back end. It usually does some background
computing for the runnable model.


Score
------

``Score`` is the abstract base class for scores. The instance of it (or its subclass) can give some types of 
results for test and/or test suite against the models.

The complete scores type in SciUnit are ``BooleanScore``, ``ZScore``, ``CohenDScore``, 
``RatioScore``, ``PercentScore``, and ``FloatScore``.

Each type of score has their own features and advantage.

There are also incomplete score types. These type does not contain any
information regarding how good the model is, but the existing of them means there are 
some issues during testing or computing process. They are ``NoneScore``, ``TBDScore``, ``NAScore``, 
and ``InsufficientDataScore``



ScoreArray, ScoreArrayM2M

Can be used like this, assuming n tests and m models:

>>> sm[test]
    (score_1, ..., score_m)

>>> sm[model]
    (score_1, ..., score_n)
    

``ScoreArray`` represents an array of scores derived from a test suite.
Extends the pandas Series such that items are either
models subject to a test or tests taken by a model.
Also displays and computes score summaries in sciunit-specific ways.

``ScoreArrayM2M`` represents an array of scores derived from ``TestM2M``.
Extends the pandas Series such that items are either
models subject to a test or the test itself.

ScoreMatrix, ScoreMatrixM2M

Can be used like this, assuming n tests and m models:

>>> sm[test]
(score_1, ..., score_m)

>>> sm[model]
(score_1, ..., score_n)


``ScoreMatrix`` represents a matrix of scores derived from a test suite.
Extends the pandas DataFrame such that tests are columns and models
are the index. Also displays and compute score summaries in sciunit-specific ways.

``ScoreMatrixM2M`` represents a matrix of scores derived from ``TestM2M``.
Extends the pandas DataFrame such that models/observation are both
columns and the index.


Test, TestM2M
--------------

``Test`` is a abstract base class for tests.

``TestM2M`` is an abstract class for handling tests involving multiple models.

A test instance contains some observations which are considered as the fact. 
The test instance can test the model by comparing the predictions with the observations 
and generate a specific type of score.

Enables comparison of model to model predictions, and also against
experimental reference data (optional).

Note: ``TestM2M`` would typically be used when handling mutliple (>2)
models, with/without experimental reference data. For single model
tests, you can use the 'Test' class.

TestSuite
----------

A collection of tests. The instance of ``TestSuite`` can perform similar things that a test instance can do.

Converter
----------

A ``Converter`` instance can be used to convert a score between two types.
It can be included in a test instance.

Capability
-----------

``Capability`` is the abstract base class for sciunit capabilities.
A capability instance can be included in a test instance to ensure the
model, which is tested by the test instance, implements some methods.
