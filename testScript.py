from elsapy import *

conFile = open("config.json")

config = json.load(conFile)

myCl = elsClient(config['apikey'])

myAuth = elsAuthor('http://api.elsevier.com/content/author/AUTHOR_ID:7004367821')
myAuth.read(myCl)
print ("myAuth.fullName: ", myAuth.fullName)

myAff = elsAffil('http://api.elsevier.com/content/affiliation/AFFILIATION_ID:60016849')
myAff.read(myCl)
print ("myAff.name: ", myAff.name)

myDoc = elsDoc('http://api.elsevier.com/content/abstract/SCOPUS_ID:84872135457')
myDoc.read(myCl)
print ("myDoc.title: ", myDoc.title)

myAuth.readDocs(myCl)
print ("myAuth.docList: ")
i = 0
for doc in myAuth.docList:
    i += 1
    print (i, ' - ', doc['dc:title'])
