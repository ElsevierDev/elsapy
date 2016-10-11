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
            "X-ELS-APIKey"  : self.apiKey,
            "User-Agent"    : self.__userAgent
            }
        r = requests.get(
            self.__base_url + pathStr + queryStr,
            headers = headers
            )
        if r.status_code == 200:
            return r.text
        else:
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

    def update(self):
        """Fetches the latest data for this entity from api.elsevier.com"""
        pass

    def getURI(self):
        """Returns the URI of the entity instance"""
        return self.uri

class elsAuthor(elsEntity):
    """An author of a document in Scopus"""

    def __init__(self, URI):
        """Initializes an author given a Scopus author ID"""
        elsEntity.__init__(self, URI)
        self.firstName = ""
        self.lastName = ""
