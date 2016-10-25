import requests, json, time
from abc import ABCMeta, abstractmethod

class elsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # class variables
    __base_url = "https://api.elsevier.com/"    ## Base URL for later use
    __userAgent = "elsapy.py"                   ## Helps track library use
    __minReqInterval = 1                        ## Min. request interval in sec
    __tsLastReq = time.time()                   ## Tracker for throttling
    numRes = 25                                 ## Max # of records per request
    
    # constructors
    def __init__(self, apiKey, instToken = ''):
        """Initializes a client with a given API Key and (optional) institutional token."""
        self.apiKey = apiKey
        self.instToken = instToken

    # properties
    @property
    def instToken(self):
        """Get the instToken for the client instance"""
        return self._instToken

    @instToken.setter
    def instToken(self, instToken):
        """Set the instToken for the client instance"""
        self._instToken = instToken

    @property
    def apiKey(self):
        """Get the apiKey for the client instance"""
        return self._apiKey

    @apiKey.setter
    def apiKey(self, apiKey):
        """Set the apiKey for the client instance"""
        self._apiKey = apiKey

    # access functions
    def getBaseURL(self):
        """Returns the ELSAPI base URL currently configured for the client"""
        return self.__base_url

    def showApiKey(self):
        """Returns the APIKey currently configured for the client"""
        return self._apiKey

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
            "X-ELS-APIKey"  : self._apiKey,
            "User-Agent"    : self.__userAgent,
            "Accept"        : 'application/json'
            }
        if self._instToken:
            headers["X-ELS-Insttoken"] = self._instToken
        r = requests.get(
            URL,
            headers = headers
            )
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise (requests.HTTPError, requests.RequestException)
            print ("HTTP " + str(r.status_code) + " Error from " + URL + " :\n" + r.text)


class elsEntity(metaclass=ABCMeta):
    """An abstract class representing an entity in Elsevier's data model"""

    # constructors
    @abstractmethod
    def __init__(self, uri):
        """Initializes a data entity with its URI"""
        self._uri = uri

    # properties
    @property
    def uri(self):
        """Get the URI of the entity instance"""
        return self._uri

    @uri.setter
    def uri(self, uri):
        """Get the URI of the entity instance"""
        self._uri = uri

    @property
    def data(self):
        """Get the full JSON data for the entity instance"""
        return self._data

    
    # modifier functions
    @abstractmethod
    def read(self, elsClient, payloadType):
        """Fetches the latest data for this entity from api.elsevier.com.
            Returns True if successful; else, False."""
        try:
            apiResponse = elsClient.execRequest(self.uri)
            # TODO: check why response is serialized differently for auth vs affil
            if isinstance(apiResponse[payloadType], list):
                self._data = apiResponse[payloadType][0]
            else:
                self._data = apiResponse[payloadType]
            self.ID = self.data["coredata"]["dc:identifier"]
            return True
        except (requests.HTTPError, requests.RequestException):
            return False


class elsProfile(elsEntity, metaclass=ABCMeta):
    """An abstract class representing an author or affiliation profile in Elsevier's data model"""

    @abstractmethod
    def readDocs(self, elsClient, payloadType):
        """Fetches the list of documents associated with this entity from
            api.elsevier.com. If need be, splits the requests in batches to
            retrieve them all. Returns True if successful; else, False."""
        try:
            apiResponse = elsClient.execRequest(self.uri + "?view=documents")
            # TODO: check why response is serialized differently for auth vs affil; refactor
            if isinstance(apiResponse[payloadType], list):
                data = apiResponse[payloadType][0]
            else:
                data = apiResponse[payloadType]
            docCount = int(data["documents"]["@total"])
            self.docList = [x for x in data["documents"]["abstract-document"]]
            for i in range (0, docCount//elsClient.numRes):
                apiResponse = elsClient.execRequest(self.uri + "?view=documents&start=" + str((i+1)*elsClient.numRes+1))
                # TODO: check why response is serialized differently for auth vs affil; refactor
                if isinstance(apiResponse[payloadType], list):
                    data = apiResponse[payloadType][0]
                else:
                    data = apiResponse[payloadType]
                self.docList = self.docList + [x for x in data["documents"]["abstract-document"]]
            return True
        except (requests.HTTPError, requests.RequestException):
            return False

class elsAuthor(elsProfile):
    """An author of a document in Scopus"""
    
    # static variables
    __payloadType = u'author-retrieval-response'

    # constructors
    def __init__(self, URI):
        """Initializes an author given a Scopus author ID"""
        elsEntity.__init__(self, URI)

    # properties
    @property
    def first_name(self):
        """Gets the author's first name"""
        return self._first_name;

    @property
    def last_name(self):
        """Gets the author's last name"""
        return self._last_name;     

    @property
    def full_name(self):
        """Gets the author's full name"""
        return self.first_name + " " + self.last_name;     

    # modifier functions
    def read(self, elsClient):
        """Reads the JSON representation of the author from ELSAPI.
            Returns True if successful; else, False."""
        if elsProfile.read(self, elsClient, self.__payloadType):
            self._first_name = self.data[u'author-profile'][u'preferred-name'][u'given-name']
            self._last_name = self.data[u'author-profile'][u'preferred-name'][u'surname']
            return True
        else:
            return False

    def readDocs(self, elsClient):
        """Fetches the list of documents associated with this author from api.elsevier.com.
             Returns True if successful; else, False."""
        return elsProfile.readDocs(self, elsClient, self.__payloadType)
        

class elsAffil(elsProfile):
    """An affilliation (i.e. an institution an author is affiliated with) in Scopus"""
    
    # static variables
    __payloadType = u'affiliation-retrieval-response'

    # constructors
    def __init__(self, URI):
        """Initializes an affiliation given a Scopus affiliation ID"""
        elsEntity.__init__(self, URI)

    # properties
    @property
    def name(self):
        """Gets the affiliation's name"""
        return self._name;     

    # modifier functions
    def read(self, elsClient):
        """Reads the JSON representation of the affiliation from ELSAPI.
             Returns True if successful; else, False."""
        if elsProfile.read(self, elsClient, self.__payloadType):
            self._name = self.data["affiliation-name"]
            return True
        else:
            return False

    def readDocs(self, elsClient):
        """Fetches the list of documents associated with this affiliation from api.elsevier.com.
             Returns True if successful; else, False."""
        return elsProfile.readDocs(self, elsClient, self.__payloadType)
        

class elsDoc(elsEntity):
    """A document in Scopus"""
    
    # static variables
    __payloadType = u'abstracts-retrieval-response'

    # constructors
    def __init__(self, URI):
        """Initializes an affiliation given a Scopus author ID"""
        elsEntity.__init__(self, URI)

    # properties
    @property
    def title(self):
        """Gets the document's title"""
        return self._title;     

    # modifier functions
    def read(self, elsClient):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if elsEntity.read(self, elsClient, self.__payloadType):
            self._title = self.data["coredata"]["dc:title"]
            return True
        else:
            return False
