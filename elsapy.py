import requests, json, time
from abc import ABCMeta, abstractmethod

class elsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # class variables
    __base_url = "https://api.elsevier.com/"    ## Base URL for later use
    __userAgent = "elsClient.py"                ## Helps track library use
    __minReqInterval = 1                        ## Min. request interval in sec
    __tsLastReq = time.time()                   ## Tracker for throttling
    numRes = 25                                 ## Max # of records per request
    
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
    def execRequest(self,URL):
        """Sends the actual request; returns response."""

        ## Throttle request, if need be
        interval = time.time() - self.__tsLastReq
        if (interval < self.__minReqInterval):
            time.sleep( self.__minReqInterval - interval )
        self.__tsLastReq = time.time()

        ## Construct and execute request
        headers = {
            "X-ELS-APIKey"  : self.__apiKey,
            "User-Agent"    : self.__userAgent,
            "Accept"        : 'application/json'
            }
        r = requests.get(
            URL,
            headers = headers
            )
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            # TODO: change to throw exception and fail 
            print ("HTTP " + str(r.status_code) + " Error from " + URL + " :\n" + r.text)


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
    @abstractmethod
    def read(self, elsClient, payloadType):
        """Fetches the latest data for this entity from api.elsevier.com"""
        # TODO: check why response is serialized differently for auth vs affil
        apiResponse = elsClient.execRequest(self.uri)
        if isinstance(apiResponse[payloadType], list):
            self.data = apiResponse[payloadType][0]
        else:
            self.data = apiResponse[payloadType]
        self.ID = self.data["coredata"]["dc:identifier"]

    @abstractmethod ## TODO: needs to be overridden in client classes so that where it is not applicable, it returns something else.
    def readDocs(self, elsClient, payloadType):
        """Fetches the list of documents associated with this entity from
            api.elsevier.com. If need be, splits the requests in batches to
            retrieve them all. """
        apiResponse = elsClient.execRequest(self.uri + "?view=documents")
        docCount = int(apiResponse[payloadType][0]["documents"]["@total"])
        self.docList = [x for x in apiResponse[payloadType][0]["documents"]["abstract-document"]]
        for i in range (0, docCount//elsClient.numRes):
            apiResponse = elsClient.execRequest(self.uri + "?view=documents&start=" + str((i+1)*elsClient.numRes+1))
            self.docList = self.docList + [x for x in apiResponse[payloadType][0]["documents"]["abstract-document"]]                                   

    # access functions
    def getURI(self):
        """Returns the URI of the entity instance"""
        return self.uri


class elsAuthor(elsEntity):
    """An author of a document in Scopus"""
    
    # static variables
    __payloadType = u'author-retrieval-response'

    # constructors
    def __init__(self, URI):
        """Initializes an author given a Scopus author ID"""
        elsEntity.__init__(self, URI)
        self.firstName = ""
        self.lastName = ""

    # modifier functions
    def read(self, elsClient):
        """Reads the JSON representation of the author from ELSAPI"""
        elsEntity.read(self, elsClient, self.__payloadType)
        self.firstName = self.data[u'author-profile'][u'preferred-name'][u'given-name']
        self.lastName = self.data[u'author-profile'][u'preferred-name'][u'surname']
        self.fullName = self.firstName + " " + self.lastName

    def readDocs(self, elsClient):
        """Fetches the list of documents associated with this author from api.elsevier.com"""
        elsEntity.readDocs(self, elsClient, self.__payloadType)
        

class elsAffil(elsEntity):
    """An affilliation (i.e. an institution an author is affiliated with) in Scopus"""
    
    # static variables
    __payloadType = u'affiliation-retrieval-response'

    # constructors
    def __init__(self, URI):
        """Initializes an affiliation given a Scopus author ID"""
        elsEntity.__init__(self, URI)

    # modifier functions
    def read(self, elsClient):
        """Reads the JSON representation of the affiliation from ELSAPI"""
        elsEntity.read(self, elsClient, self.__payloadType)
        self.name = self.data["affiliation-name"]


class elsDoc(elsEntity):
    """A document in Scopus"""
    
    # static variables
    __payloadType = u'abstracts-retrieval-response'

    # constructors
    def __init__(self, URI):
        """Initializes an affiliation given a Scopus author ID"""
        elsEntity.__init__(self, URI)

    # modifier functions
    def read(self, elsClient):
        """Reads the JSON representation of the document from ELSAPI"""
        elsEntity.read(self, elsClient, self.__payloadType)
        self.title = self.data["coredata"]["dc:title"]
