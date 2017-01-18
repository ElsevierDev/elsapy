"""The document module of elsapy.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""


import requests, json, urllib
from abc import ABCMeta, abstractmethod
from pathlib import Path
from . import log_util
from .elsclient import ElsClient
from .elsentity import ElsEntity

logger = log_util.get_logger(__name__)

class FullDoc(ElsEntity):
    """A document in ScienceDirect. Initialize with PII or DOI."""

    # static variables
    __payload_type = u'full-text-retrieval-response'
    __uri_base = u'https://api.elsevier.com/content/article/'

    @property
    def title(self):
        """Gets the document's title"""
        return self.data["coredata"]["dc:title"];

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
    def read(self, elsClient = None):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if ElsEntity.read(self, self.__payload_type, elsClient):
            return True
        else:
            return False

class AbsDoc(ElsEntity):
    """A document in Scopus. Initialize with URI or Scopus ID."""

    # static variables
    __payload_type = u'abstracts-retrieval-response'
    __uri_base = u'https://api.elsevier.com/content/abstract/'

    @property
    def title(self):
        """Gets the document's title"""
        return self.data["coredata"]["dc:title"];

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
    def read(self, elsClient = None):
        """Reads the JSON representation of the document from ELSAPI.
             Returns True if successful; else, False."""
        if ElsEntity.read(self, self.__payload_type, elsClient):
            return True
        else:
            return False