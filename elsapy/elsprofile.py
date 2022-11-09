"""The author/affiliation profile module of elsapy.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""

import requests, json, urllib, pandas as pd
from abc import ABCMeta, abstractmethod
from . import log_util
from .elsentity import ElsEntity
from .utils import recast_df


logger = log_util.get_logger(__name__)        
        
class ElsProfile(ElsEntity, metaclass=ABCMeta):
    """An abstract class representing an author or affiliation profile in
        Elsevier's data model"""

    def __init__(self, uri):
        """Initializes a data entity with its URI"""
        super().__init__(uri)
        self._doc_list = None


    @property
    def doc_list(self):
        """Get the list of documents for this entity"""
        return self._doc_list

    @abstractmethod
    def read_docs(self, payloadType, els_client = None):
        """Fetches the list of documents associated with this entity from
            api.elsevier.com. If need be, splits the requests in batches to
            retrieve them all. Returns True if successful; else, False.
			NOTE: this method requires elevated API permissions.
			See http://bit.ly/2leirnq for more info."""
        if els_client:
            self._client = els_client;
        elif not self.client:
            raise ValueError('''Entity object not currently bound to els_client instance. Call .read() with els_client argument or set .client attribute.''')
        try:
            api_response = self.client.exec_request(self.uri + "?view=documents")
            if isinstance(api_response[payloadType], list):
                data = api_response[payloadType][0]
            else:
                data = api_response[payloadType]
            docCount = int(data["documents"]["@total"])
            self._doc_list = [x for x in data["documents"]["abstract-document"]]
            for i in range (0, docCount//self.client.num_res):
                try:
                    api_response = self.client.exec_request(self.uri + "?view=documents&startref=" + str((i+1) * self.client.num_res+1))
                    if isinstance(api_response[payloadType], list):
                        data = api_response[payloadType][0]
                    else:
                        data = api_response[payloadType]
                    self._doc_list = self._doc_list + [x for x in data["documents"]["abstract-document"]]
                except  (requests.HTTPError, requests.RequestException) as e:
                    if hasattr(self, 'doc_list'):       ## We don't want incomplete doc lists
                        self._doc_list = None
                    raise e
            logger.info("Documents loaded for " + self.uri)
            self.docsframe = recast_df(pd.DataFrame(self._doc_list))
            logger.info("Documents loaded into dataframe for " + self.uri)
            return True
        except (requests.HTTPError, requests.RequestException) as e:
            logger.warning(e.args)
            return False

    def write_docs(self):
        """If a doclist exists for the entity, writes it to disk as a JSON file
             with the url-encoded URI as the filename and returns True. Else,
             returns False."""
        if self.doc_list:
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
    _payload_type = u'author-retrieval-response'
    _uri_base = u'https://api.elsevier.com/content/author/author_id/'

    # constructors
    def __init__(self, uri = '', author_id = ''):
        """Initializes an author given a Scopus author URI or author ID"""
        if uri and not author_id:
            super().__init__(uri)
        elif author_id and not uri:
            super().__init__(self._uri_base + str(author_id))
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
    def read(self, els_client = None):
        """Reads the JSON representation of the author from ELSAPI.
            Returns True if successful; else, False."""
        if ElsProfile.read(self, self._payload_type, els_client):
            return True
        else:
            return False

    def read_docs(self, els_client = None):
        """Fetches the list of documents associated with this author from 
             api.elsevier.com. Returns True if successful; else, False."""
        return ElsProfile.read_docs(self, self._payload_type, els_client)

    def read_metrics(self, els_client = None):
        """Reads the bibliographic metrics for this author from api.elsevier.com
             and updates self.data with them. Returns True if successful; else,
             False."""
        try:
            fields = [
                    "document-count",
                    "cited-by-count",
                    "citation-count",
                    "h-index",
                    "dc:identifier",
                    ]
            api_response = els_client.exec_request(
                    self.uri + "?field=" + ",".join(fields))
            data = api_response[self._payload_type][0]
            if not self.data:
                self._data = dict()
                self._data['coredata'] = dict()
            # TODO: apply decorator for type conversion of common fields
            self._data['coredata']['dc:identifier'] = data['coredata']['dc:identifier']
            self._data['coredata']['citation-count'] = int(data['coredata']['citation-count'])
            self._data['coredata']['cited-by-count'] = int(data['coredata']['citation-count'])
            self._data['coredata']['document-count'] = int(data['coredata']['document-count'])
            self._data['h-index'] = int(data['h-index'])
            logger.info('Added/updated author metrics')
        except (requests.HTTPError, requests.RequestException) as e:
            logger.warning(e.args)
            return False
        return True

        
class ElsAffil(ElsProfile):
    """An affilliation (i.e. an institution an author is affiliated with) in Scopus.
        Initialize with URI or affiliation ID."""
    
    # static variables
    _payload_type = u'affiliation-retrieval-response'
    _uri_base = u'https://api.elsevier.com/content/affiliation/affiliation_id/'

    # constructors
    def __init__(self, uri = '', affil_id = ''):
        """Initializes an affiliation given a Scopus affiliation URI or affiliation ID."""
        if uri and not affil_id:
            super().__init__(uri)
        elif affil_id and not uri:
            super().__init__(self._uri_base + str(affil_id))
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
    def read(self, els_client = None):
        """Reads the JSON representation of the affiliation from ELSAPI.
             Returns True if successful; else, False."""
        if ElsProfile.read(self, self._payload_type, els_client):
            return True
        else:
            return False

    def read_docs(self, els_client = None):
        """Fetches the list of documents associated with this affiliation from
              api.elsevier.com. Returns True if successful; else, False."""
        return ElsProfile.read_docs(self, self._payload_type, els_client)
