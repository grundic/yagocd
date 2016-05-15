|gocd_logo| Yet another GoCD python client
==========================================

    .. image:: https://travis-ci.org/grundic/yagocd.svg?branch=master
       :target: https://travis-ci.org/grundic/yagocd

    .. image:: https://coveralls.io/repos/github/grundic/yagocd/badge.svg?branch=master
       :target: https://coveralls.io/github/grundic/yagocd?branch=master

    .. image:: https://badge.fury.io/py/yagocd.svg
       :target: https://badge.fury.io/py/yagocd

Introduction
------------
This project represent itself high level wrapper upon ThoughtWorks GoCD REST API.
Go Continuous Delivery is continues integration/deployment server, which helps you automate
and streamline the build-test-release cycle for worry-free.
Using this library you can access to internals of the Pipelines, check their statuses, download Artifacts and more.

Library has a :code:`Yagocd` class, which is a single entry point of whole project. Creating instance of it would give you
possibilities to work with all functionality.

Installation
------------
.. code-block:: bash

    $ pip install yagocd

Quick example
-------------

.. code:: python

    from yagocd import Yagocd

    go = Yagocd(
        server='https://example.com',
        auth=('user', 'password'),
        options={
            'verify': False # skip verification for SSL certificates.
        }
    )

    for pipeline in go.pipelines.list():
        for instance in pipeline.history():
            for stage in instance.stages():
                for job in stage.jobs():
                    # print artifact urls for each job
                    for artifact in job.artifact.list():
                        for file_obj in artifact.files():
                            print(file_obj.data.url)

                    # print property of each job
                    for key, value in job.prop.list().items():
                        print "{} => {}".format(key, value)



Code Organisation
-----------------
The code in the library organized as follows: the main entry point, that user should use is :code:`yagocd.client.Yagocd`
class. Creating instance of it gives you access to all properties and actions GoCD server provides.
This class contains list of managers, each of which is responsible for it's particular area. Each manager could be
accessed as a property of :code:`Yagocd` class. Here is list of them:

- :code:`agents`: manage build agents
- :code:`configurations`: manage configuration
- :code:`feeds`: work with feeds
- :code:`materials`: list,modify and notify materials
- :code:`pipelines`: work with pipelines
- :code:`properties`: work with job's properties
- :code:`stages`: work with stages
- :code:`users`: manage users

Each of managers wraps REST API calls in functions. Depending on return value, it could be possible to get instance of
another class, that will provide additional functionality.
For example, :code:`yagocd.resources.pipeline.PipelineManager` manager could return instance of
:code:`yagocd.resources.pipeline.PipelineEntity`, which represents itself entity of specific pipeline and has
corresponding methods.

Different implementations of GoCD API
-------------------------------------
Here is list of similar projects, that implements GoCD API:

- [python] `py-gocd <https://github.com/gaqzi/py-gocd/>`_: A Python API for interacting with Go Continuous Delivery
- [python] `gocdapi <https://github.com/joaogbcravo/gocdapi>`_: A Python API for accessing resources and configuring Go (thoughtworks) continuous-delivery servers
- [python]   `gomatic <https://github.com/SpringerSBM/gomatic>`_: A Python API for configuring GoCD
- [ruby] `goapi <https://github.com/ThoughtWorksStudios/goapi>`_: Go (http://www.go.cd) API ruby client
- [NodeJS] `gocd-api <https://github.com/birgitta410/gocd-api>`_: Access http://www.go.cd API via nodeJS
- [GoLang] `gocd-api <https://github.com/christer79/gocd-api>`_: An implementation of the gocd API

Development notes
-----------------

Original API is part of the open source `GoCD project <https://github.com/gocd/gocd>`_.
But it's difficult to find appropriate implementation.

- First, there are url rewrite rules in `/server/webapp/WEB-INF/urlrewrite.xml <https://github.com/gocd/gocd/blob/master/server/webapp/WEB-INF/urlrewrite.xml>`_ in <!-- RESTful URLS --> section.
- Second, there is `/server/webapp/WEB-INF/rails.new/config/routes.rb <https://github.com/gocd/gocd/blob/master/server/webapp/WEB-INF/rails.new/config/routes.rb>`_ file, in which some routes are set as well.
- Third, in `/server/src/com/thoughtworks/go/server/controller <https://github.com/gocd/gocd/tree/master/server/src/com/thoughtworks/go/server/controller>`_ folder there is implementation of all API endpoints, but with different interfaces and URLs (which are handled by aforementioned configs).

Using this information could give better understanding of internals of Go server for future development and support.

Running local server
--------------------

As described in `this post <https://www.go.cd/2015/08/05/Go-Sample-Virtualbox.html>`_, there is ready to use
Virtual Box image with pre-configured GoCD server and agent, which could easy development and debugging.
To run, executing this command (ensure, that vagrant and Virtual Box are installed):

.. code-block:: bash

    $ vagrant init gocd/gocd-demo

In the current directory will be created :code:`Vagrantfile` with initial content. I recommend forward ports:

.. code-block :: ruby

    config.vm.network "forwarded_port", guest: 8153, host: 8153
    config.vm.network "forwarded_port", guest: 8154, host: 8154

One for `http`, another for `https` -- this will make it possible to use it from https://localhost:8154/go/ url.
After that run

.. code-block:: bash

    $ vagrant up

and wait some time for machine to load and service to be up.

.. |gocd_logo| image:: https://raw.githubusercontent.com/grundic/yagocd/master/img/gocd_logo.png
