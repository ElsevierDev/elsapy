"""An example program that uses the elsapy module"""

from elsapy import *

## Load configuration
conFile = open("config.json")
config = json.load(conFile)
conFile.close()

## Initialize client
myCl = elsClient(config['apikey'])
myCl.inst_token = config['insttoken']

## Initialize search object
mySrch = elsSearch('heart','scopus')

## Execute search and show results
mySrch.execute(myCl)
print (mySrch.apiResponse)

#### Author example
### Initialize author with uri
##myAuth = elsAuthor(uri = 'http://api.elsevier.com/content/author/AUTHOR_ID/7004367821')
### Read author data, then write to disk
##if myAuth.read(myCl):
##    print ("myAuth.full_name: ", myAuth.full_name)
##    myAuth.write()
##else:
##    print ("Read author failed.")
##
#### Affiliation example
### Initialize affiliation with ID as string
##myAff = elsAffil(affil_id = '60101411')
##if myAff.read(myCl):
##    print ("myAff.name: ", myAff.name)
##    myAff.write()
##else:
##    print ("Read affiliation failed.")
##
#### Document example
### Initialize document with ID as integer
##myDoc = elsDoc(scp_id = 84872135457)
##if myDoc.read(myCl):
##    print ("myDoc.title: ", myDoc.title)
##    myDoc.write()   
##else:
##    print ("Read document failed.")
##
#### Load list of documents from the API into affilation and author objects.
### Since a document list is retrieved for 25 entries at a time, this is
###  a potentially lenghty operation - hence the prompt.
##print ("Load documents (Y/N)?")
##s = input('--> ')
##
##if (s == "y" or s == "Y"):
##
##    ## Read all documents for example author, then write to disk
##    if myAuth.readDocs(myCl):
##        print ("myAuth.doc_list has " + str(len(myAuth.doc_list)) + " items.")
##        myAuth.writeDocs()
##    else:
##        print ("Read docs for author failed.")
##
##    ## Read all documents for example affiliation, then write to disk
##    if myAff.readDocs(myCl):
##        print ("myAff.doc_list has " + str(len(myAff.doc_list)) + " items.")
##        myAff.writeDocs()
##    else:
##        print ("Read docs for affiliation failed.")
