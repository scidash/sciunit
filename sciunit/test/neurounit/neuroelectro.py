import sciunit
from urllib2 import urlopen
import json

API_VERSION = 1
API_SUFFIX = '/api/%d/nes/?' % API_VERSION
DEVELOPER = True
if DEVELOPER:
	DOMAIN = 'http://localhost:8000'
else:
	DOMAIN = 'http://www.neuroelectro.org'
API_URL = DOMAIN+API_SUFFIX

# Creates a test based on neuroelectro.org data using that site's API.  
class NeuroElectroTest(sciunit.Test):
	neuron_id = None
	ephysprop_id = None 
	neuron_name = None
	ephysprop_name = None
	#mean = None
	#sd = None
	def set_neuron(self,nlex_id): # Sets the biological neuron using a NeuroLex ID.  
		self.neuron_id = nlex_id
	def set_ephysprop(self,nlex_id): # Sets the electrophysiological property type using a NeuroLex ID.  NOTE: There are no such IDs for ephys properties currently.  
		self.ephysprop_id = nlex_id
	def get_json(self,params=None): # Gets JSON data from neuroelectro.org based on the currently set neuron and ephys property.  Use 'params' to constrain the data returned.  
		url = API_URL # Base URL.  
		# Create the full URL.  
		if self.neuron_id is not None:
			url += "nlex=%s&" % self.neuron_id # Change this for consistency in the neuroelectro.org API.  
		if self.ephysprop_id is not None:
			url += "e__nlexid=%s&" % self.ephysprop_id
		url_result = urlopen(url) # Get the page.  
		html = url_result.read() # Read out the HTML (actually JSON)
		self.json_object = json.loads(html) # Convert into a JSON object.  
	def get_values(self,params=None): # Gets values from neuroelectro.org.  We will use 'params' in the future to specify metadata (e.g. temperature) that neuroelectro.org will provide.  
		self.get_json(params=params)
		data = self.json_object['objects'] # All the summary matches in neuroelectro.org for this combination of neuron and ephys property.  
		data = data[0] # For now, we are just going to take the first match.  If neuron_id and ephysprop_id where both specified, there should be only one anyway.  
		self.neuron_name = data['neuron']['name'] # Set the neuron name from the json data.  
		self.ephysprop_name = data['ephysprop']['name'] # Set the ephys property name from the json data.  
		self.mean = data['value_mean']
		self.sd = data['value_sd']
	def check(self):
		try:
			mean = self.mean
			sd = self.sd
		except AttributeError as a:
			print 'The mean and sd were not found.'
			raise
	def run(self):
		# Compare the model ephys property to that mean and sd.  
		# Compute a p-value.  
		# Return a score (some transformation of the p-value).  
			
