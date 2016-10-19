from elsapy import *

conFile = open("config.json")

config = json.load(conFile)

myCl = elsClient(config['apikey'])

myAuth = elsAuthor('http://api.elsevier.com/content/author/AUTHOR_ID:55934026500')
myAuth.read(myCl)

myAff = elsAffil('http://api.elsevier.com/content/affiliation/AFFILIATION_ID:60016849')
myAff.read(myCl)

myDoc = elsDoc('http://api.elsevier.com/content/abstract/SCOPUS_ID:84872135457')
myDoc.read(myCl)

myAuth.readDocs(myCl)
