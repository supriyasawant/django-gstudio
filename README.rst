==================
gstudio: Gnowledge Studio
==================

A collaborative workspace for constructing and publishing semantic
knowledge networks and ontologies is being constructed. 

Features taking shape
========

As and when a feature is tested and working it will be listed below.

Nodes implemented:
================
* metaTypes
* objectTypes
* objects
* relations
* relationtypes
* attributes
* attributetypes

All the nodes above are also registered with django-reversion for
version control. 

In our next release we will add dependency relation, and create
appropriate fields for relations and atttributes.  While we shape this
project, if you are interested in joining, visit us at metastudio.org.

Nodes soon to come:
==================
* system (ontology)
* systemtype (ontologytype)

Features you will see soon:
===========================
* dependency relation 
* context graphs and concept graphs

Other features to come:
======================

* rdf feed to a triple store
* export and import of standard knowledge representation languages: CL, OWL, XTM etc.

Features adopted from Django-Blog-Zinnia
=======================================
The following features are adopted from django-blog-zinnia code base
with a lot of gratitude.  Thanks to an excellent codebase of
django-blog-zinnia, which taught us best software development
practices as well! After reviewing each feature for the purpose of
semantic blogging, we will retain or extend the following features.

* Comments
* `Sitemaps`_
* Archives views
* Related entries
* Private entries
* RSS or Atom Feeds
* Tags and categories views
* `Advanced search engine`_
* Prepublication and expiration
* Edition in `MarkDown`_, `Textile`_ or `reStructuredText`_
* Widgets (Popular entries, Similar entries, ...)
* Spam protection with `Akismet`_ or `TypePad`_
* Admin dashboard
* `MetaWeblog API`_
* Ping Directories
* Ping External links
* `Bit.ly`_ support
* `Twitter`_ support
* `Gravatar`_ support
* `Django-CMS`_ plugins
* Collaborative work
* Tags autocompletion
* `Entry model extendable`_
* Pingback/Trackback support
* `Blogger conversion utility`_
* `WordPress conversion utility`_
* `WYMeditor`_, `TinyMCE`_ and `MarkItUp`_ support
* Ready to use and extendables templates
* `Windows Live Writer`_ compatibility

Examples
========

We will soon create a sandbox site for users to play and test the features.

Project Page
================

https://www.metastudio.org/groups/gstudio/overview
