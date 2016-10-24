from elsapy import *

## Load configuration
conFile = open("config.json")
config = json.load(conFile)
conFile.close()

## Initialize client
myCl = elsClient(config['apikey'],config['insttoken'])

## Initialize and read example author
myAuth = elsAuthor('http://api.elsevier.com/content/author/AUTHOR_ID:7004367821')       ## author with more than 25 docs
if myAuth.read(myCl):
    print ("myAuth.fullName: ", myAuth.fullName)

## Initialize and read example affiliation
myAff = elsAffil('http://api.elsevier.com/content/affiliation/AFFILIATION_ID:60101411')
if myAff.read(myCl):
    print ("myAff.name: ", myAff.name)

## Initialize and read example document
myDoc = elsDoc('http://api.elsevier.com/content/abstract/SCOPUS_ID:84872135457')
if myDoc.read(myCl):
    print ("myDoc.title: ", myDoc.title)


## Read all documents for example author
if myAuth.readDocs(myCl):
    print ("myAuth.docList: ")
    i = 0
    for doc in myAuth.docList:
        i += 1
        print (i, ' - ', doc['dc:title'])

## Read all documents for example affiliation
if myAff.readDocs(myCl):
    print ("myAff.docList: ")
    i = 0
    for doc in myAff.docList:
        i += 1
        print (i, ' - ', doc['dc:title'])


