"""
Base class for SciUnit models, and various examples
"""

import inspect
import random
from fnmatch import fnmatchcase

from cypy import memoize # Decorator for caching of capability method results.  

from .base import SciUnit
from .utils import class_intern,method_cache
from .capabilities import Capability,ProducesNumber

class Model(SciUnit):
    """Abstract base class for sciunit models."""
    def __init__(self, name=None, **params):
        if name is None:
            name = self.__class__.__name__
        self.name = name
        self.params = params
        if params is None:
            params = {}
        super(Model,self).__init__()
        self.check_params()

    name = None
    """The name of the model. Defaults to the class name."""

    description = ""
    """A description of the model."""

    params = None
    """The parameters to the model (a dictionary).
    These distinguish one model of a class from another."""

    run_args = None
    """These are the run-time arguments for the model.
    Execution of run() should make use of these arguments."""

    @property
    def capabilities(self):
        capabilities = []
        for cls in self.__class__.mro():
            if issubclass(cls,Capability) and cls is not Capability \
            and not issubclass(cls,Model):
                capabilities.append(cls.__name__)
        return capabilities 

    def describe(self):
        result = "No description available"
        if self.description:
            result = "%s" % self.description
        else:
            if self.__doc__:
                s = []
                s += [self.__doc__.strip().replace('\n','').replace('    ','')]
                result = '\n'.join(s)
        return result

    def curr_method(self, back=0):
        return(inspect.stack()[1+back][3])

    def check_params(self):
        """Check model parameters to see if they are reasonable.
        e.g. they would check self.params to see if a particular value
        was within an acceptable range.  This should be implemented
        as needed by specific model classes.
        """
        pass

    def is_match(self, match):
        result = False
        if self == match:
            result = True
        elif isinstance(match,str) and fnmatchcase(self.name, match):
            result = True # Found by instance or name
        return result

    def __str__(self):
        return '%s' % self.name


class ConstModel(Model,ProducesNumber):
    """A model that always produces a constant number as output."""
    
    def __init__(self, constant, name=None):
        self.constant = constant 
        super(ConstModel, self).__init__(name=name, constant=constant)
        
    def produce_number(self):
        return self.constant


class UniformModel(Model,ProducesNumber):
    """A model that always produces a random uniformly distributed number
    in [a,b] as output."""
    
    def __init__(self, a, b, name=None):
        self.a, self.b = a, b
        super(UniformModel, self).__init__(name=name, a=a, b=b)
    
    def produce_number(self):
        return random.uniform(self.a, self.b)


################################################################
# Here are several examples of caching and sharing can be used
# to reduce the computational load of testing.  
################################################################

class UniqueRandomNumberModel(Model,ProducesNumber):
    """An example model to ProducesNumber."""

    def produce_number(self):
        """Each call to this method will produce a different random number."""
        return random.random()


class RepeatedRandomNumberModel(Model,ProducesNumber):
    """An example model to demonstrate ProducesNumber with cypy.lazy."""

    @memoize
    def produce_number(self):
        """Each call to this method will produce the same random number as
        was returned in the first call, ensuring reproducibility and
        eliminating computational overhead."""
        return random.random()


@class_intern
class SharedModel(Model):
    """A model that, each time it is instantiated with the same parameters, will
    return the same instance at the same locaiton in memory. 
    Attributes should not be set post-instantiation
    unless the goal is to set those attributes on all models of this class."""
    pass


class PersistentUniformModel(UniformModel):
    """TODO"""
    
    def run(self):
        self._x = random.uniform(self.a, self.b)

    def produce_number(self):
        return self._x


class CacheByInstancePersistentUniformModel(PersistentUniformModel):
    """TODO"""
    
    @method_cache(by='instance',method='run')
    def produce_number(self):
        return self._x


class CacheByValuePersistentUniformModel(PersistentUniformModel):
    """TODO"""
    
    @method_cache(by='value',method='run')
    def produce_number(self):
        return self._x