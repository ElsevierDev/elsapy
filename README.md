# elsapy

A Python module for use with api.elsevier.com. Its aim is to make life easier for people who are not primarily programmers, but need to interact with publication and citation data from Elsevier products in a programmatic manner (e.g. academic researchers). The module consists of the following classes:

* elsClient: represents a client interface to api.elsevier.com.
* elsEntity: an abstract class representing an entity in the Elsevier (specifically, Scopus) data model. elsEntities can be initialized with a URI, after which they can read their own data from api.elsevier.com through an elsClient instance. elsEntity has the following descendants:
	* elsProf: an abstract class representing a _profiled_ entity in Scopus. This class has two descendants:
		* elsAuthor: represent the author of one or more documents in Scopus.
		* elsAffil: represents an affiliation (i.e. an institution authors are affiliated with) in Scopus
	* elsDoc: represents a document in Scopus. This document typically is the record of a scholarly article in any of the journals covered in Scopus.

Each elsEntity (once read) has a .data attribute, which contains a JSON/dictionary representation of the object's data. Use the object's .data.keys() method to list the first-level keys in the dictionary; drill down from there to explore the data.

More info on the Scopus data model can be read [here](https://dev.elsevier.com/tecdoc_ir_cris_vivo.html). Over time, the module will be expanded to also cover access to ScienceDirect content.

## Prerequisites
*   An API key from http://dev.elsevier.com
*   Python 3.x on your machine, with the [Requests HTTP library](http://docs.python-requests.org/) added
*   A network connection at an institution that subscribes to Scopus
*	Some knowledge of Python and [object-oriented design](https://en.wikipedia.org/wiki/Object-oriented_design)

## Quick start
*   Add your APIkey to config.json
*   Modify testScript.py to suit your needs