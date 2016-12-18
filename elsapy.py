"""A Python module for use with api.elsevier.com. Its aim is to make life easier
    for people who are not primarily programmers, but need to interact with
    publication and citation data from Elsevier products in a programmatic
    manner (e.g. academic researchers).
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * http://dev.elsevier.com
    * http://api.elsevier.com"""

__version__ = '0.1'

import requests, json, time, logging, urllib
from abc import ABCMeta, abstractmethod
from pathlib import Path

## Following adapted from https://docs.python.org/3/howto/logging-cookbook.html
# create logger with module name
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create log path, if not already there
logPath = Path('logs')
if not logPath.exists():
	logPath.mkdir()
# create file handler which logs even debug messages
fh = logging.FileHandler('logs/elsapy-%s.log' % time.strftime('%Y%m%d'))
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info("Module loaded.")

class ElsClient:
    """A class that implements a Python interface to api.elsevier.com"""

    # class variables
    __url_base = "https://api.elsevier.com/"    ## Base URL for later use
    __user_agent = "elsapy-v%s" % __version__   ## Helps track library use
    __min_req_interval = 1                      ## Min. request interval in sec
    __ts_last_req = time.time()                 ## Tracker for throttling
    
    
    # constructors
    def __init__(self, api_key, inst_token = '', num_res = 25):
        """Initializes a client with a given API Key and (optional) institutional token."""
        self.api_key = api_key
        self.inst_token = inst_token
        self.num_res = num_res

    # properties
    @property
    def api_key(self):
        """Get the apiKey for the client instance"""
        return self._api_key
    @api_key.setter
    def api_key(self, api_key):
        """Set the apiKey for the client instance"""
        self._api_key = api_key

    @property
    def inst_token(self):
        """Get the instToken for the client instance"""
        return self._inst_token
    @inst_token.setter
    def inst_token(self, inst_token):
        """Set the instToken for the client instance"""
        self._inst_token = inst_token

    @property
    def num_res(self):
        """Gets the max. number of results to be used by the client instance"""
        return self._num_res
    
    @num_res.setter
    def num_res(self, numRes):
        """Sets the max. number of results to be used by the client instance"""
        self._num_res = numRes


    # access functions
    def getBaseURL(self):
        """Returns the ELSAPI base URL currently configured for the client"""
        return self.__url_base

    # request/response execution functions
    def execRequest(self,URL):
        """Sends the actual request; returns response."""

        ## Throttle request, if need be
        interval = time.time() - self.__ts_last_req
        if (interval < self.__min_req_interval):
            time.sleep( self.__min_req_interval - interval )
        
        ## Construct and execute request
        headers = {
            "X-ELS-APIKey"  : self.api_key,
            "User-Agent"    : self.__user_agent,
            "Accept"        : 'application/json'
            }
        if self.inst_token:
            headers["X-ELS-Insttoken"] = self.inst_token
        logger.info('Sending GET request to ' + URL)
        r = requests.get(
            URL,
            headers = headers
            )
        self.__ts_last_req = time.time()
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise requests.HTTPError("HTTP " + str(r.status_code) + " Error from " + URL + " :\n" + r.text)
            

class ElsEntity(metaclass=ABCMeta):
    """An abstract class representing an entity in Elsevier's data model"""

    # constructors
    @abstractmethod
    def __init__(self, uri):
        """Initializes a data entity with its URI"""
        self._uri = uri
        self._data = None

    # properties
    @property
    def uri(self):
        """Get the URI of the entity instance"""
        return self._uri

    @uri.setter
    def uri(self, uri):
        """Set the URI of the entity instance"""
        self._uri = uri

    @property
    def data(self):
        """Get the full JSON data for the entity instance"""
        return self._data

    
    # modifier functions
    @abstractmethod
    def read(self, ElsClient, payloadType):
        """Fetches the latest data for this entity from api.elsevier.com.
            Returns True if successful; else, False."""
        try:
            apiResponse = ElsClient.execRequest(self.uri)
            # TODO: check why response is serialized differently for auth vs affil
            if isinstance(apiResponse[payloadType], list):
                self._data = apiResponse[payloadType][0]
            else:
                self._data = apiResponse[payloadType]
            self.ID = self.data["coredata"]["dc:identifier"]
            ## TODO: check if URI is the same, if necessary update and log warning
            logger.info("Data loaded for " + self.uri)
            return True
        except (requests.HTTPError, requests.RequestException)as e:
            logger.warning(e.args)
            return False

    def write(self):
        """If data exists for the entity, writes it to disk as a .JSON file with
             the url-encoded URI as the filename and returns True. Else, returns
             False."""
        if (self.data):
            dataPath = Path('data')
            if not dataPath.exists():
                    dataPath.mkdir()
            dump_file = open('data/'+urllib.parse.quote_plus(self.uri)+'.json', mode='w')
            json.dump(self.data, dump_file)
            dump_file.close()
            logger.info('Wrote ' + self.uri + ' to file')
            return True
        else:
            logger.warning('No data to write for ' + self.uri)
            return False
        
class ElsProfile(ElsEntity, metaclass=ABCMeta):
    """An abstract class representing an author or affiliation profile in
        Elsevier's data model"""

    def __init__(self, uri):
        """Initializes a data entity with its URI"""
        ElsEntity.__init__(self, uri)
        self._doc_list = None


    @property
    def doc_list(self):
        """Get the list of documents for this entity"""
        return self._doc_list

    @abstractmethod
    def readDocs(self, ElsClient, payloadType):
        """Fetches the list of documents associated with this entity from
            api.elsevier.com. If need be, splits the requests in batches to
            retrieve them all. Returns True if successful; else, False."""
        try:
            apiResponse = ElsClient.execRequest(self.uri + "?view=documents")
            # TODO: check why response is serialized differently for auth vs affil; refactor
            if isinstance(apiResponse[payloadType], list):
                data = apiResponse[payloadType][0]
            else:
                data = apiResponse[payloadType]
            docCount = int(data["documents"]["@total"])
            self._doc_list = [x for x in data["documents"]["abstract-document"]]
            for i in range (0, docCount//ElsClient.num_res):
                try:
                    apiResponse = ElsClient.execRequest(self.uri + "?view=documents&start=" + str((i+1)*ElsClient.num_res+1))
                    # TODO: check why response is serialized differently for auth vs affil; refactor
                    if isinstance(apiResponse[payloadType], list):
                        data = apiResponse[payloadType][0]
                    else:
                        data = apiResponse[payloadType]
                    self._doc_list = self._doc_list + [x for x in data["documents"]["abstract-document"]]
                except  (requests.HTTPError, requests.RequestException) as e:
                    if hasattr(self, 'doc_list'):       ## We don't want incomplete doc lists
                        self._doc_list = None
                    raise e
            logger.info("Documents loaded for " + self.uri)
            return True
        except (requests.HTTPError, requests.RequestException) as e:
            logger.warning(e.args)
            return False

    def writeDocs(self):
        """If a doclist exists for the entity, writes it to disk as a .JSON file
             with the url-encoded URI as the filename and returns True. Else,
             returns False."""
        if self.doc_list:
            dataPath = Path('data')
            if not dataPath.exists():
                    dataPath.mkdir()
            dump_file = open('data/'
                             + urllib.parse.quote_plus(self.uri+'?view=documents')
                             + '.json', mode='w'
                             )
            dump_file.write('[' + json.dumps(self.doc_list[0]))
            for i in range (1, len(self.doc_list)):
                dump_file.write(',' + json.dumps(self.doc_list[i]))
            dump_file.write(']')
            dump_file.close()
            logger.info('Wrote ' + self.uri + '?view=documents to file')
            return True
        else:
            logger.warning('No doclist to write for ' + self.uri)
            return False


class ElsAuthor(ElsProfile):
    """An author of a document in Scopus. Initialize with URI or author ID."""
    
    # static variables
    __payload_type = u'author-retrieval-response'
    __uri_base = u'http://api.elsevier.com/content/author/AUTHOR_ID/'

    # constructors
    def __init__(self, uri = '', author_id = ''):
        """Initializes an author given a Scopus author URI or author ID"""
        if uri and not author_id:
            ElsEntity.__init__(self, uri)
        elif author_id and not uri:
            ElsEntity.__init__(self, self.__uri_base + str(author_id))
        elif not uri and not author_id:
            raise ValueError('No URI or author ID specified')
        else:
            raise ValueError('Both URI and author ID specified; just need one.')

    # properties
    @property
    def first_name(self):
        """Gets the author's first name"""
        return self.data[u'author-profile'][u'preferred-name'][u'given-name']

    @property
    def last_name(self):
        """Gets the author's last name"""
        return self.data[u'author-profile'][u'preferred-name'][u'surname']    

    @property
    def full_name(self):
        """Gets the author's full name"""
        return self.first_name + " " + self.last_name    

    # modifier functions
    def read(self, ElsClient):
        """Reads the JSON representation of the author from ELSAPI.
            Returns True if successful; else, False."""
        if ElsProfile.read(self, ElsClient, self.__payload_type):
            return True
        else:
            return False

    def readDocs(self, ElsClient):
        """Fetches the list of documents associated with this author from 
             api.elsevier.com. Returns True if successful; else, False."""
        return ElsProfile.readDocs(self, ElsClient, self.__payload_type)

    def readMetrics(self, ElsClient):
        """Reads the bibliographic metrics for this author from api.elsevier.com
             and updates self.data with them. Returns True if successful; else,
             False."""
        try:
            apiResponse = ElsClient.execRequest(self.uri + "?field=document-count,cited-by-count,citation-count,h-index")
            data = apiResponse[self.__payload_type][0]
            self._data['coredata']['citation-count'] = data['coredata']['citation-count']
            self._data['coredata']['cited-by-count'] = data['coredata']['citation-count']
            self._data['coredata']['document-count'] = data['coredata']['document-count']
            self._data['h-index'] = data['h-index']
            logger.info('Added/updated author metrics')
        except (requests.HTTPError, requests.RequestException) as e:
            logger.warning(e.args)
            return False
        return True

class ElsAffil(ElsProfile):
    """An affilliation (i.e. an institution an author is affiliated with) in Scopus.
        Initialize with URI or affiliation ID."""
    
    # static variables
    __payload_type = u'affiliation-retrieval-response'
    __uri_base = u'http://api.elsevier.com/content/affiliation/AFFILIATION_ID/'

    # constructors
    def __init__(self, uri = '', affil_id = ''):
        """Initializes an affiliation given a Scopus affiliation URI or affiliation ID."""
        if uri and not affil_id:
            ElsProfile.__init__(self, uri)
        elif affil_id and not uri:
            ElsProfile.__init__(self, self.__uri_base + str(affil_id))
        elif not uri and not affil_id:
            raise ValueError('No URI or affiliation ID specified')
        else:
            raise ValueError('Both URI and affiliation ID specified; just need one.')

    # properties
    @property
    def name(self):
        """Gets the affiliation's name"""
        return self.data["affiliation-name"];     

    # modifier functions
    def read(self, ElsClient):
        """Reads the JSON representation of the affiliation from ELSAPI.
             Returns True if successful; else, False."""
        if ElsProfile.read(self, ElsClient, self.__payload_type):
            return True
        else:
            return False

    def readDocs(self, ElsClient):
        """Fetches the list of documents associated with this affiliation from
              api.elsevier.com. Returns True if successful; else, False."""
        return ElsProfile.readDocs(self, ElsClient, self.__payload_type)



class FullDoc(ElsEntity):
    """A document in ScienceDirect. Initialize with PII or DOI."""

    # static variables
    __payload_type = u'full-text-retrieval-response'
    __uri_base = u'http://api.elsevier.com/content/article/'

    @property
    def title(self):
        """Gets the document's title"""
        return self._title;

    @property
    def uri(self):
        """Gets the document's uri"""
        return self._uri

    # constructors
    def __init__(self, uri = '', sd_pii = '', doi = ''):
        """Initializes a document given a Scopus document URI or Scopus ID."""
        if uri and not sd_pii and not doi:
            ElsEntity.__init__(self, uri)
        elif sd_pii and not uri and not doi:
            ElsEntity.__init__(self, self.__uri_base + 'PII/' + str(sd_pii))
        elif doi and not uri and not sd_pii:
            ElsEntity.__init__(self, self.__uri_base + 'DOI/' + str(doi))
        elif not uri and not scp_id and not doi:
            raise ValueError('No URI, ScienceDirect PII or DOI specified')
        else:
            raise ValueError('Multiple identifiers specified; just need one.')

    # modifier functions
    def read(self, ElsClient):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if ElsEntity.read(self, ElsClient, self.__payload_type):
            self._title = self.data["coredata"]["dc:title"]
            return True
        else:
            return False

class AbsDoc(ElsEntity):
    """A document in Scopus. Initialize with URI or Scopus ID."""

    # static variables
    __payload_type = u'abstracts-retrieval-response'
    __uri_base = u'http://api.elsevier.com/content/abstract/'

    @property
    def title(self):
        """Gets the document's title"""
        return self._title;

    @property
    def uri(self):
        """Gets the document's uri"""
        return self._uri

    # constructors
    def __init__(self, uri = '', scp_id = ''):
        """Initializes a document given a Scopus document URI or Scopus ID."""
        if uri and not scp_id:
            ElsEntity.__init__(self, uri)
        elif scp_id and not uri:
            ElsEntity.__init__(self, self.__uri_base + 'SCOPUS_ID/' + str(scp_id))
        elif not uri and not scp_id:
            raise ValueError('No URI or Scopus ID specified')
        else:
            raise ValueError('Both URI and Scopus ID specified; just need one.')    

    # modifier functions
    def read(self, ElsClient):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if ElsEntity.read(self, ElsClient, self.__payload_type):
            self._title = self.data["coredata"]["dc:title"]
            return True
        else:
            return False


class ElsDoc():
    """A document in Scopus and/or ScienceDirect. Initialize with Scopus ID, PII or DOI; or with a
        dictionary containing multiple api.elsevier.com URIs."""

    # static variables

    def __init__(self, uris = '', scp_id = '', sd_pii = '', doi = ''):
        if uris and not scp_id and not sd_pii and not doi:
            self._uris = uris
        ## The following 'elif' clauses leverage other classes to transform
        ##  'bare' IDs to corresponding URIs before storing them in the URI
        ##  dictionary
        elif scp_id and not uris and not sd_pii and not doi:
            self._uris = {'scp_id' : AbsDoc(scp_id = scp_id).uri}
        elif sd_pii and not scp_id and not uris and not doi:
            self._uris = {'sd_pii' : FullDoc(sd_pii = sd_pii).uri}
        elif doi and not scp_id and not uris and not sd_pii:
            self._uris = {'doi' : FullDoc(doi = doi).uri}

    # properties
    ## TODO: add more property getters/setters that map ElsDoc properties to AbsDoc and FullDoc properties.
    @property
    def title(self):
        """Gets the document's title. The title from the full-text record takes precedence over
            the title from the Scopus abstract record."""
        try:
            return self._fullDoc.title
        except AttributeError:
            try:
                return self._absDoc.title
            except AttributeError:
                raise AttributeError("'ElsDoc' object has no attribute 'title'")

    @property
    def uris(self):
        """Gets the document's uri dictionary"""
        return self._uris

    def read(self, ElsClient):
        """Reads JSON representations of the document from ELSAPI for whichever
            URIs exist in the URI dictionary. Returns True if successful; else,
            False."""
        success = False
        if 'scp_id' in self.uris:
            self._absDoc = AbsDoc(uri = self.uris['scp_id'])
            success = self._absDoc.read(ElsClient)
        if 'sd_pii' in self.uris:
            self._fullDoc = FullDoc(uri = self.uris['sd_pii'])
            success = self._fullDoc.read(ElsClient)
        elif 'doi' in self.uris:
            self._fullDoc = FullDoc(uri = self.uris['doi'])
            success = self._fullDoc.read(ElsClient)
        return success

class ElsSearch():
    """Represents a search to one of the search indexes accessible
         through api.elsevier.com. Returns True if successful; else, False."""

    # static variables
    __base_url = u'http://api.elsevier.com/content/search/'

    def __init__(self, query, index):
        """Initializes a search object with a query and target index."""
        self.query = query
        self.index = index
        self._uri = self.__base_url + self.index + '?query=' + self.query

    # properties
    @property
    def query(self):
        """Gets the search query"""
        return self._query

    @query.setter
    def query(self, query):
        """Sets the search query"""
        self._query = query

    @property
    def index(self):
        """Gets the label of the index targeted by the search"""
        return self._index

    @index.setter
    def index(self, index):
        self._index = index
        """Sets the label of the index targeted by the search"""

    @property
    def results(self):
        """Gets the results for the search"""
        return self._results

    @property
    def tot_num_res(self):
        """Gets the total number of results that exist in the index for
            this query. This number might be larger than can be retrieved
            and stored in a single ElsSearch object (i.e. 5,000)."""
        return self._tot_num_res

    @property
    def num_res(self):
        """Gets the number of results for this query that are stored in the 
            search object. This number might be smaller than the number of 
            results that exist in the index for the query."""
        return len(self.results)

    @property
    def uri(self):
        """Gets the request uri for the search"""
        return self._uri

    def execute(self, ElsClient, get_all = False):
        """Executes the search. If get_all = False (default), this retrieves
            the default number of results specified for the API. If
            get_all = True, multiple API calls will be made to iteratively get 
            all results for the search, up to a maximum of 5,000."""
        apiResponse = ElsClient.execRequest(self._uri)
        self._tot_num_res = int(apiResponse['search-results']['opensearch:totalResults'])
        self._results = apiResponse['search-results']['entry']
        if get_all is True:
            while (self.num_res < self.tot_num_res) and (self.num_res < 5000):
                for e in apiResponse['search-results']['link']:
                    if e['@ref'] == 'next':
                        next_url = e['@href']
                apiResponse = ElsClient.execRequest(next_url)
                self._results += apiResponse['search-results']['entry']         

    def hasAllResults(self):
        """Returns true if the search object has retrieved all results for the
            query from the index (i.e. num_res equals tot_num_res)."""
        return (self.num_res is self.tot_num_res)
