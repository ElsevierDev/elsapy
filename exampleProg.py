"""An example program that uses the elsapy module"""

from elsapy import *

## Load configuration
conFile = open("config.json")
config = json.load(conFile)
conFile.close()

## Initialize client
myCl = ElsClient(config['apikey'])
myCl.inst_token = config['insttoken']

## Initialize search object
mySrch = ElsSearch('heart','scopus')

## Execute search and show results
mySrch.execute(myCl)
#print (mySrch.apiResponse)
