# elsapy

A Python module for use with api.elsevier.com. Its aim is to make life easier for people who are not primarily programmers, but need to interact with publication and citation data from Elsevier products in a programmatic manner (e.g. academic researchers). The module consists of the following classes:

* ElsClient: represents a [client interface to api.elsevier.com](https://github.com/ElsevierDev/elsapy/wiki/Establishing-an-API-interface-for-your-program).
* ElsEntity: an abstract class representing an entity in the Elsevier (specifically, Scopus) data model. ElsEntities can be initialized with a URI, after which they can read their own data from api.elsevier.com through an ElsClient instance. ElsEntity has the following descendants:
	* elsProf: an abstract class representing a _profiled_ entity in Scopus. This class has two descendants:
		* ElsAuthor: represent the author of one or more documents in Scopus.
		* ElsAffil: represents an affiliation (i.e. an institution authors are affiliated with) in Scopus
	* AbsDoc: represents a document in Scopus (i.e. abstract only). This document typically is the record of a scholarly article in any of the journals covered in Scopus.
	* FullDoc: represents a document in ScienceDirect (i.e. full text). This document is the full-text version of a scholarly article or book chapter from a journal published by Elsevier.

	Each ElsEntity (once read) has a .data attribute, which contains a JSON/dictionary representation of the object's data. Use the object's .data.keys() method to list the first-level keys in the dictionary; drill down from there to explore the data.

	ElsAuthor and ElsAffil objects also have a method, .readDocs(), that tells it to retrieve all the publications associated with that author/affiliation from Elsevier's API, and store it as a list attribute, .doc_list. Each entry in the list is a dictionary containing that document's metadata.
* ElsSearch: represents a search through one of Elsevier's indexes, which can be a document index (ScienceDirect or Scopus), an author index, or an affiliation index. Once executed, each search object has a list attribute, .results, that contains the results retrieved from Elsevier's APIs for that search. Each entry in the list is a dictionary containing that result's metadata.

More info on the [wiki](https://github.com/ElsevierDev/elsapy/wiki).

## Prerequisites
*   An API key from http://dev.elsevier.com
*   Python 3.x on your machine, with the [Requests HTTP library](http://docs.python-requests.org/) added. If you have neither installed yet, you might want to get the [Anaconda distribution of Python 3.6](https://www.continuum.io/downloads) go get both in one go (plus a lot of other useful stuff)
*   A network connection at an institution that subscribes to Scopus and/or ScienceDirect
*   Some knowledge of Python and [object-oriented design](https://en.wikipedia.org/wiki/Object-oriented_design)

## Quick start
*   Download or clone this repository (elsapy is not yet available through `pip install`)
*   Add the unzipped / cloned 'elsapy' folder to your Python package folder, or to your project's folder
*   Create a [config file and add your APIkey](https://github.com/ElsevierDev/elsapy/blob/master/CONFIG.md) to it
*   Modify exampleProg.py to suit your needs

## Disclaimer
This is not an 'official' SDK and is not guaranteed to always work with Elsevier's APIs, on all platforms, or without eating up all your machine's resources. But we'll do our best to keep it in good shape, are happy to take suggestions for improvements, and are open to collaborations. License info is [here](https://github.com/ElsevierDev/elsapy/blob/master/LICENSE.md).
