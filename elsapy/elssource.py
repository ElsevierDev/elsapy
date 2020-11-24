from abc import ABCMeta, abstractmethod
from .elsentity import ElsEntity

class ElsSource(ElsEntity):
    """An serial in Scopus. Initialize with URI or source ISSN."""
    
    # static variables
    _payload_type = 'serial-metadata-response'
    _uri_base = u'https://api.elsevier.com/content/serial/title/issn/'

    # constructors
    def __init__(self, uri = '', serial_issn = ''):
        """Initializes a serial given a Scopus source URI or serial ISSN"""
        if uri and not serial_issn:
            super().__init__(uri)
        elif serial_issn and not uri:
            super().__init__(self._uri_base + str(serial_issn))
        elif not uri and not serial_issn:
            raise ValueError('No URI or ISSN specified')
        else:
            raise ValueError('Both URI and ISSN specified; just need one.')

    # properties
    @property
    def title(self):
        """Gets the serial's title"""
        return self.data[u'entry'][0][u'dc:title']
    
    # modifier functions
    def read(self, els_client = None):
        """Reads the JSON representation of the author from ELSAPI.
            Returns True if successful; else, False."""
        if ElsEntity.read(self, self._payload_type, els_client):
            return True
        else:
            return False
