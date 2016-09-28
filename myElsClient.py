import requests


class myElsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # local variables
    __base_url = "https://api.elsevier.com/"

    # constructors
    def __init__(self, apiKey):
        """Instantiates a client with a given API Key."""
        self.apiKey = apiKey

    # configuration functions
    def setInstToken(self, instToken):
        """Sets an institutional token for customer authentication"""
        self.instToken = instToken

    # utility access functions
    def getBaseURL(self):
        """Returns the base URL currently configured for Elsevier's APIs"""
        return self.__base_url

    # request/response execution functions
    def execRequest(self,pathStr,queryStr):
        """Constructs and sends the actual request; returns response."""
        headers = {
            "X-ELS-APIKey" : self.apiKey
            }
        r = requests.get(
            self.__base_url + pathStr + queryStr,
            headers = headers
            )
        if r.status_code == 200:
            return r
        else:
            print "error"
