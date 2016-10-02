.. yagocd documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to GoCD Python API client's documentation!
==================================================

Intro
-----

This `library <https://github.com/grundic/yagocd>`_ is a high level python API wrapper upon ThoughtWorks GoCD REST API.

Here are some highlights:

- it's created and designed with simplicity in mind, so it would be easy to start using it.
- there is only one class, that you would need to initialize and work with.
- pipelines are linked together, so you can iterate over predecessors or descendants of a given pipeline.
- it's very close to the original REST API implementation from ThoughtWorks.
- every class and function is annotated with ``@since`` decorator, which gives possibility to check at runtime
  whether specific feature is supported on given server version.
- it's possible to use latest library version with any GoCD server version, even if some parameters or headers
  are different: we have special methods to pass correct parameters depending on the server version.
- *every* version of GoCD is meticulously tested, thanks to releases of it in Docker container. Here is a list
  of versions supported so far:

  - 16.1.0
  - 16.2.1
  - 16.3.0
  - 16.6.0
  - 16.7.0
  - 16.8.0
  - 16.9.0

  Older version should work as well, but as they are not supported and there is no Docker images for them, you should
  use them on your own risk.

Contents:
---------

.. toctree::
   :maxdepth: 2

   readme
   usage
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

