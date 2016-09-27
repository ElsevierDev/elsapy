import requests


class myElsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # local variables
    __base_url = "http://api.elsevier.com/"
    
    def __init__(self, apiKey):
        """Instantiates a client with a given API Key."""
        self.apiKey = apiKey

    def getBaseURL(self):
        return self.__base_url
