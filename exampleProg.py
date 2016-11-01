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
