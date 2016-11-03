# elsapy

A Python module for use with api.elsevier.com. Its aim is to make life easier for people who are not primarily programmers, but need to interact with publication and citation data from Elsevier products in a programmatic manner (e.g. academic researchers). The module consists of the following classes:

* ElsClient: represents a client interface to api.elsevier.com.
* ElsEntity: an abstract class representing an entity in the Elsevier (specifically, Scopus) data model. ElsEntities can be initialized with a URI, after which they can read their own data from api.elsevier.com through an ElsClient instance. ElsEntity has the following descendants:
	* elsProf: an abstract class representing a _profiled_ entity in Scopus. This class has two descendants:
		* ElsAuthor: represent the author of one or more documents in Scopus.
		* ElsAffil: represents an affiliation (i.e. an institution authors are affiliated with) in Scopus
	* ElsDoc: represents a document in Scopus. This document typically is the record of a scholarly article in any of the journals covered in Scopus.

    Each ElsEntity (once read) has a .data attribute, which contains a JSON/dictionary representation of the object's data. Use the object's .data.keys() method to list the first-level keys in the dictionary; drill down from there to explore the data.
* ElsSearch: represents a search through one of Elsevier's indexes, which can be a document index, an author index, or an affiliation index.

More info on the Scopus data model can be read [here](https://dev.elsevier.com/tecdoc_ir_cris_vivo.html). Over time, the module will be expanded to also cover access to ScienceDirect content.

## Prerequisites
*   An API key from http://dev.elsevier.com
*   Python 3.x on your machine, with the [Requests HTTP library](http://docs.python-requests.org/) added
*   A network connection at an institution that subscribes to Scopus
*	Some knowledge of Python and [object-oriented design](https://en.wikipedia.org/wiki/Object-oriented_design)

## Quick start
*   Add your APIkey to config.json
*   Modify testScript.py to suit your needs

## Disclaimer
This is not an 'official' SDK and is not guaranteed to always work with Elsevier's APIs, on all platforms, or without eating up all your machine's resources. But we'll do our best to keep it in good shape, are happy to take suggestions for improvements, and are open to collaborations.
