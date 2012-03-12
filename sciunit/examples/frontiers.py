'''
Examples from the Frontiers paper.
'''

import sciunit
import numpy as np

class ReceivesCurrent(sciunit.Capability):
    def set_current(self, current):
        raise NotImplementedError("Must implement set_current.")
    
class ProducesFiringRate(sciunit.Capability):
    def get_firing_rate(self):
        raise NotImplementedError("Must implement get_firing_rate.")

class RateTestGenerator(sciunit.BooleanTest):
    def __init__(self, mean, std, input_currents):
        self.mean = mean
        self.std = std
        self.input_currents = input_currents
        num_samples, num_timesteps = input_currents.shape
        self.num_samples = num_samples
        self.num_timesteps = num_timesteps
        
    def run_test(self, model):
        # Capability checks
        sciunit.require(model, ReceivesCurrent, ProducesFiringRate)
        
        # Execution 
        num_samples = self.num_samples
        currents = self.get_input_currents()
        mean_rates = np.empty((num_samples,))
        
        for i, current in enumerate(currents):
            model.set_current(current)
            rate = model.get_firing_rate()
            mean_rates[i] = np.mean(rate)

        model_mean = np.mean(mean_rates)
            
        # Validation
        mean, std = self.mean, self.std
        return (mean - std) <= model_mean <= (mean + std)
    
    def get_input_currents(self):
        input_currents = self.input_currents
        for i in xrange(self.num_samples):
            yield input_currents[i, :]
    