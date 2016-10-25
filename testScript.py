from elsapy import *

## Load configuration
conFile = open("config.json")
config = json.load(conFile)
conFile.close()

## Initialize client
myCl = elsClient(config['apikey'])
myCl.instToken = config['insttoken']

## Initialize and read example author
myAuth = elsAuthor('http://api.elsevier.com/content/author/AUTHOR_ID:7004367821')       ## author with more than 25 docs
if myAuth.read(myCl):
    print ("myAuth.full_name: ", myAuth.full_name)

## Initialize and read example affiliation
myAff = elsAffil('http://api.elsevier.com/content/affiliation/AFFILIATION_ID:60101411')
if myAff.read(myCl):
    print ("myAff.name: ", myAff.name)

## Initialize and read example document
myDoc = elsDoc('http://api.elsevier.com/content/abstract/SCOPUS_ID:84872135457')
if myDoc.read(myCl):
    print ("myDoc.title: ", myDoc.title)

print ("Load documents (Y/N)?")
s = input('--> ')

if (s == "y" or s == "Y"):

    ## Read all documents for example author
    if myAuth.readDocs(myCl):
        print ("myAuth.doc_list: ")
        i = 0
        for doc in myAuth.doc_list:
            i += 1
            print (i, ' - ', doc['dc:title'])

    ## Read all documents for example affiliation
    if myAff.readDocs(myCl):
        print ("myAff.doc_list: ")
        i = 0
        for doc in myAff.doc_list:
            i += 1
            print (i, ' - ', doc['dc:title'])
