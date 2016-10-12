import requests
from abc import ABCMeta, abstractmethod

class myElsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # static variables
    __base_url = "https://api.elsevier.com/"
    __userAgent = "myElsClient.py"
    
    # constructors
    def __init__(self, apiKey):
        """Initializes a client with a given API Key."""
        self.__apiKey = apiKey

    # configuration functions
    def setInstToken(self, instToken):
        """Sets an institutional token for customer authentication"""
        self.instToken = instToken

    # access functions
    def getBaseURL(self):
        """Returns the ELSAPI base URL currently configured for the client"""
        return self.__base_url

    # access functions
    def showApiKey(self):
        """Returns the APIKey currently configured for the client"""
        return self.__apiKey
    

    # request/response execution functions
    def execRequest(self,URI):
        """Sends the actual request; returns response."""
        headers = {
            "X-ELS-APIKey"  : self.__apiKey,
            "User-Agent"    : self.__userAgent,
            "Accept"        : 'application/json'
            }
        r = requests.get(
            URI,
            headers = headers
            )
        if r.status_code == 200:
            # TODO: change to parse JSON
            return r.text
        else:
            # TODO: change to throw exception and fail gracefully
            return "HTTP " + str(r.status_code) + " Error: \n" + r.text


class elsEntity:
    """An abstract class representing an entity in Elsevier's data model"""
    
    # make class abstract
    __metaclass__ = ABCMeta

    # constructors
    @abstractmethod
    def __init__(self, URI):
        """Initializes a data entity with its URI"""
        self.uri = URI

    # modifier functions
    def update(self, myElsClient):
        """Fetches the latest data for this entity from api.elsevier.com"""
        return myElsClient.execRequest(self.uri)

    # access functions
    def getURI(self):
        """Returns the URI of the entity instance"""
        return self.uri

class elsAuthor(elsEntity):
    """An author of a document in Scopus"""

    # constructors
    def __init__(self, URI):
        """Initializes an author given a Scopus author ID"""
        elsEntity.__init__(self, URI)
        self.firstName = ""
        self.lastName = ""
