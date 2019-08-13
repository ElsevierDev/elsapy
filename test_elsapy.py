"""Test cases for elsapy"""

## TODO:
## - break down in modules (test suites) for each class to allow faster unit-testing
## - this will require a shared 'utility class'
## - add a module that integrates all

from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
from urllib.parse import quote_plus as url_encode
import json, pathlib

## Load good client configuration
conFile = open("config.json")
config = json.load(conFile)
conFile.close()

## Set local path for test data and ensure it's clean
test_path = pathlib.Path.cwd() / 'test_data'
if not test_path.exists():
    test_path.mkdir()
else:
    file_list = list(test_path.glob('*'))
    ## TODO: write recursive function that also identifies and clears out child directories
    for e in file_list:
        if e.is_file():
            e.unlink()
            
class util:
    """Contains tests common to test cases from multiple classes"""
    
    def file_exist_with_id(id):
        """Test case: exactly one local file exist with given ID in the filename"""
        if len(list(test_path.glob('*' + id +'*'))) == 1:
            return True


class TestElsClient:
    """Test general client functionality"""
    
    def test_init_apikey_(self):
        """Test case: APIkey and token are set correctly during initialization"""
        my_client = ElsClient(config['apikey'])
        assert my_client.api_key == config['apikey']
        assert my_client.inst_token == None
        
    def test_init_apikey_insttoken(self):
        """Test case: APIkey and insttoken are set correctly during initialization"""
        my_client = ElsClient(config['apikey'], inst_token = config['insttoken'])
        assert my_client.api_key == config['apikey']
        assert my_client.inst_token == config['insttoken']
        
    def test_init_apikey_insttoken_path(self):
        """Test case: APIkey, insttoken and local path are set correctly during initialization"""
        loc_dir = '\\TEMP'
        my_client = ElsClient(config['apikey'], inst_token = config['insttoken'], local_dir = loc_dir)
        assert my_client.api_key == config['apikey']
        assert my_client.inst_token == config['insttoken']
        assert str(my_client.local_dir) == loc_dir
        
    def test_set_apikey_insttoken(self):
        """Test case: APIkey and insttoken are set correctly using setters"""
        my_client = ElsClient("dummy")
        my_client.api_key = config['apikey']
        my_client.inst_token = config['insttoken']
        assert my_client.api_key == config['apikey']
        assert my_client.inst_token == config['insttoken']

class TestElsAuthor:
    """Test author object functionality"""
    
    ## Test data
    auth_uri = "https://api.elsevier.com/content/author/author_id/55070335500"
    auth_id_int = 55070335500
    auth_id_str = "55070335500"

    ## Test initialization
    def test_init_uri(self):
        """ Test case: uri is set correctly during initialization with uri"""
        myAuth = ElsAuthor(uri = self.auth_uri)
        assert myAuth.uri == self.auth_uri
        
    def test_init_auth_id_int(self):
        """ Test case: uri is set correctly during initialization with author id as integer"""
        myAuth = ElsAuthor(author_id = self.auth_id_int)
        assert myAuth.uri == self.auth_uri
        
    def test_init_auth_id_str(self):
        """ Test case: uri is set correctly during initialization with author id as string"""
        myAuth = ElsAuthor(author_id = self.auth_id_str)
        assert myAuth.uri == self.auth_uri
        
    ## Test reading/writing author profile data
    bad_client = ElsClient("dummy")
    good_client = ElsClient(config['apikey'], inst_token = config['insttoken'])
    good_client.local_dir = str(test_path)

    myAuth = ElsAuthor(uri = auth_uri)
    
    def test_read_good_bad_client(self):
        """Test case: using a well-configured client leads to successful read
            and using a badly-configured client does not."""
        assert self.myAuth.read(self.bad_client) == False
        assert self.myAuth.read(self.good_client) == True

    def test_json_to_dict(self):
        """Test case: the JSON read by the author object from the API is parsed
            into a Python dictionary"""
        assert type(self.myAuth.data) == dict
        
    def test_name_getter(self):
        """Test case: the full name attribute is returned as a non-empty string"""
        assert (type(self.myAuth.full_name) == str and self.myAuth.full_name != '')
        
    def test_write(self):
        """Test case: the author object's data is written to a file with the author
            ID in the filename"""
        self.myAuth.write()
        assert util.file_exist_with_id(self.myAuth.data['coredata']['dc:identifier'].split(':')[1])

    def test_read_docs(self):
        self.myAuth.read_docs()
        assert len(self.myAuth.doc_list) > 0
        ## TODO: once author metrics inconsistency is resolved, change to: 
        # assert len(self.myAuth.doc_list) == int(self.myAuth.data['coredata']['document-count'])
        
    def test_read_metrics_new_author(self):
        myAuth = ElsAuthor(uri = self.auth_uri)
        myAuth.read_metrics(self.good_client)
        assert (
            myAuth.data['coredata']['citation-count'] and  
            myAuth.data['coredata']['cited-by-count'] and 
            myAuth.data['coredata']['document-count'] and 
            myAuth.data['h-index'])
            
    def test_read_metrics_existing_author(self):
        self.myAuth.read_metrics(self.good_client)
        assert (
            self.myAuth.data['coredata']['citation-count'] and  
            self.myAuth.data['coredata']['cited-by-count'] and 
            self.myAuth.data['coredata']['document-count'] and 
            self.myAuth.data['h-index'])
        
            
class TestElsAffil:
    """Test affiliation functionality"""
    
    ## Test data
    aff_uri = "https://api.elsevier.com/content/affiliation/affiliation_id/60101411"
    aff_id_int = 60101411
    aff_id_str = "60101411"
    
    ## Test initialization
    def test_init_uri(self):
        """ Test case: uri is set correctly during initialization with uri"""
        myAff = ElsAffil(uri = self.aff_uri)
        assert myAff.uri == self.aff_uri
        
    def test_init_aff_id_int(self):
        """ Test case: uri is set correctly during initialization with affiliation id as integer"""
        myAff = ElsAffil(affil_id = self.aff_id_int)
        assert myAff.uri == self.aff_uri
        
    def test_init_aff_id_str(self):
        """ Test case: uri is set correctly during initialization with affiliation id as string"""
        myAff = ElsAffil(affil_id = self.aff_id_str)
        assert myAff.uri == self.aff_uri
        
    ## Test reading/writing author profile data
    bad_client = ElsClient("dummy")
    good_client = ElsClient(config['apikey'], inst_token = config['insttoken'])
    good_client.local_dir = str(test_path)

    myAff = ElsAffil(uri = aff_uri)
    
    def test_read_good_bad_client(self):
        """Test case: using a well-configured client leads to successful read
            and using a badly-configured client does not."""
        assert self.myAff.read(self.bad_client) == False
        assert self.myAff.read(self.good_client) == True

    def test_json_to_dict(self):
        """Test case: the JSON read by the author object from the API is parsed
            into a Python dictionary"""
        assert type(self.myAff.data) == dict
        
    def test_name_getter(self):
        """Test case: the name attribute is returned as a non-empty string"""
        assert (type(self.myAff.name) == str and self.myAff.name != '')
        
    def test_write(self):
        """Test case: the author object's data is written to a file with the author
            ID in the filename"""
        self.myAff.write()
        assert util.file_exist_with_id(self.myAff.data['coredata']['dc:identifier'].split(':')[1])

    def test_read_docs(self):
        self.myAff.read_docs()
        assert len(self.myAff.doc_list) == int(self.myAff.data['coredata']['document-count'])
            
 
class TestAbsDoc:
    """Test Scopus document functionality"""
    
    ## Test data
    abs_uri = "https://api.elsevier.com/content/abstract/scopus_id/84872135457"
    scp_id_int = 84872135457
    scp_id_str = "84872135457"
    
    ## Test initialization
    def test_init_uri(self):
        """ Test case: uri is set correctly during initialization with uri"""
        myAbsDoc = AbsDoc(uri = self.abs_uri)
        assert myAbsDoc.uri == self.abs_uri
        
    def test_init_scp_id_int(self):
        """ Test case: uri is set correctly during initialization with Scopus id as integer"""
        myAbsDoc = AbsDoc(scp_id = self.scp_id_int)
        assert myAbsDoc.uri == self.abs_uri
        
    def test_init_scp_id_str(self):
        """ Test case: uri is set correctly during initialization with Scopus id as string"""
        myAbsDoc = AbsDoc(scp_id = self.scp_id_str)
        assert myAbsDoc.uri == self.abs_uri
        
    ## Test reading/writing author profile data
    bad_client = ElsClient("dummy")
    good_client = ElsClient(config['apikey'], inst_token = config['insttoken'])
    good_client.local_dir = str(test_path)

    myAbsDoc = AbsDoc(uri = abs_uri)
    
    def test_read_good_bad_client(self):
        """Test case: using a well-configured client leads to successful read
            and using a badly-configured client does not."""
        assert self.myAbsDoc.read(self.bad_client) == False
        assert self.myAbsDoc.read(self.good_client) == True

    def test_json_to_dict(self):
        """Test case: the JSON read by the abstract document object from the 
            API is parsed into a Python dictionary"""
        assert type(self.myAbsDoc.data) == dict
        
    def test_title_getter(self):
        """Test case: the title attribute is returned as a non-empty string"""
        assert (type(self.myAbsDoc.title) == str and self.myAbsDoc.title != '')
        
    def test_write(self):
        """Test case: the abstract document object's data is written to a file with the Scopus
            ID in the filename"""
        self.myAbsDoc.write()
        assert util.file_exist_with_id(self.myAbsDoc.data['coredata']['dc:identifier'].split(':')[1])

class TestFullDoc:
    """Test ScienceDirect article functionality"""
    
    ## Test data
    full_pii_uri = "https://api.elsevier.com/content/article/pii/S1674927814000082"
    sd_pii = 'S1674927814000082'
    full_doi_uri = "https://api.elsevier.com/content/article/doi/10.1016/S1525-1578(10)60571-5"
    doi = '10.1016/S1525-1578(10)60571-5'
    
    ## Test initialization
    def test_init_uri(self):
        """ Test case: uri is set correctly during initialization with uri"""
        myFullDoc = FullDoc(uri = self.full_pii_uri)
        assert myFullDoc.uri == self.full_pii_uri
        
    def test_init_sd_pii(self):
        """ Test case: uri is set correctly during initialization with ScienceDirect PII"""
        myFullDoc = FullDoc(sd_pii = self.sd_pii)
        assert myFullDoc.uri == self.full_pii_uri
        
    def test_init_doi(self):
        """ Test case: uri is set correctly during initialization with DOI"""
        myFullDoc = FullDoc(doi = self.doi)
        assert myFullDoc.uri == self.full_doi_uri
        
    ## Test reading/writing author profile data
    bad_client = ElsClient("dummy")
    good_client = ElsClient(config['apikey'], inst_token = config['insttoken'])
    good_client.local_dir = str(test_path)

    myFullDoc = FullDoc(uri = full_pii_uri)
    
    def test_read_good_bad_client(self):
        """Test case: using a well-configured client leads to successful read
            and using a badly-configured client does not."""
        assert self.myFullDoc.read(self.bad_client) == False
        assert self.myFullDoc.read(self.good_client) == True

    def test_json_to_dict(self):
        """Test case: the JSON read by the full article object from the 
            API is parsed into a Python dictionary"""
        assert type(self.myFullDoc.data) == dict
        
    def test_title_getter(self):
        """Test case: the title attribute is returned as a non-empty string"""
        assert (type(self.myFullDoc.title) == str and self.myFullDoc.title != '')
        
    def test_write(self):
        """Test case: the full article object's data is written to a file with the ID in the filename"""
        self.myFullDoc.write()
        ## TODO: replace following (strung-together replace) with regex
        assert util.file_exist_with_id(
                self.myFullDoc.data['coredata']['pii'].replace('-','').replace('(','').replace(')',''))
 

 
class TestSearch:
    """Test search functionality"""

    ## Test data
    base_url = u'https://api.elsevier.com/content/search/'
    search_types = [
     {"query" : "authlast(keuskamp)", "index" : "author"},
     {"query" : "affil(amsterdam)", "index" : "affiliation"},
     {"query" : "AFFIL(dartmouth) AND AUTHOR-NAME(lewis) AND PUBYEAR > 2011",
              "index" : "scopus"},
     {"query" : "star trek vs star wars", "index" : "sciencedirect"}
    ]
    
    searches = [ ElsSearch(search_type["query"], search_type["index"])
        for search_type in search_types]
    
    good_client = ElsClient(config['apikey'], inst_token = config['insttoken'])

        
    ## Test initialization
    def test_init_uri(self):
        """Test case: query, index and uri are set correctly during
        initialization"""
        match_all = True
        for i in range(len(self.search_types)):
            if (self.searches[i].query != self.search_types[i]['query'] or 
                self.searches[i].index != self.search_types[i]['index'] or
                self.searches[i].uri != (self.base_url + 
                             self.search_types[i]['index'] + 
                             '?query=' + 
                             url_encode(self.search_types[i]['query']))):
                match_all = False
        assert match_all == True
    
    def test_execution(self):
        '''Test case: all searches are executed without raising an exception.'''
        for search in self.searches:
            search.execute(self.good_client)
        assert True
