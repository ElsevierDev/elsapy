# elsapy

A Python library for use with api.elsevier.com, containing the following classes:

* elsClient: represents a client interface to api.elsevier.com
* elsEntity: an abstract class representing an entity in the Elsevier (specifically, Scopus) data model. elsEntities can be initialized with a URI, after which they can read their own data from api.elsevier.com through an elsClient instance. elsEntity has the following descendants:
	* elsAuthor: represent the author of one or more documents in Scopus.
	* elsAffil: represents an affiliation (i.e. an institution authors are affiliated with) in Scopus
	* elsDoc: represents a document in Scopus. This document typically is the record of a scholarly article in any of the journals covered in Scopus.

More info on the Scopus data model can be read [here](https://dev.elsevier.com/tecdoc_ir_cris_vivo.html).