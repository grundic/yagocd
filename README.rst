Yet another gocd python client
==============================

Introduction
------------
This project represent itself high level wrapper upon ThoughtWorks gocd REST API.
Go Continuous Delivery is continues integration/deployment server, which helps you automate
and streamline the build-test-release cycle for worry-free.
Using this library you can access to internals of the Pipelines, check their statuses, download Artifacts and more.

Library has a `Client` class, which is a single entry point of whole project. Creating instance of it would give you
possibilities to work with all functionality.

Installation
------------
.. code-block:: bash

    $ pip install requests

Examples
--------
Create instance of `yagocd.client.Client`
*****************************************

.. code:: python

    go = Client(
        server='https://example.com',
        auth=('user', 'password'),
        options={
            'verify': False # skip verification for SSL certificates.
        }
    )

List of available managers of the client, accessible as it's properties:
* `agents`: manage build agents
* `configurations`: manage configuration
* `feeds`: work with feeds
* `materials`: list,modify and notify materials
* `pipelines`: work with pipelines
* `properties`: work with job's properties
* `stages`: work with stages
* `users`: manage users

Pipeline
********

.. code:: python

    # list pipelines
    print(go.pipelines.list())

Code Organisation
-----------------

Development notes
-----------------

Original API is part of the open source `GOCD project <https://github.com/gocd/gocd>`_.
But it's difficult to find appropriate implementation.
* First, there are url rewrite rules in
`/server/webapp/WEB-INF/urlrewrite.xml <https://github.com/gocd/gocd/blob/master/server/webapp/WEB-INF/urlrewrite.xml>`_
in <!-- RESTful URLS --> section.
* Second, there is `/server/webapp/WEB-INF/rails.new/config/routes.rb <https://github.com/gocd/gocd/blob/master/server/webapp/WEB-INF/rails.new/config/routes.rb>`_
file, in which some routes are set as well.
* Third, in `/server/src/com/thoughtworks/go/server/controller <https://github.com/gocd/gocd/tree/master/server/src/com/thoughtworks/go/server/controller>`_
folder there is implementation of all API endpoints, but with different interfaces and URLs (which are handled
by aforementioned configs).

Using this information could give better understanding of internals of Go server for future development and support.

Running local server
--------------------

As described in `this post <https://www.go.cd/2015/08/05/Go-Sample-Virtualbox.html>`_, there is ready to use
Virtual Box image with pre-configured GoCD server and agent, which could easy development and debugging.
To run, executing this command (ensure, that vagrant and Virtual Box are installed):
```
vagrant init gocd/gocd-demo
```

In the current directory will be created `Vagrantfile` with initial content. I recommend forward ports:
```
config.vm.network "forwarded_port", guest: 8153, host: 8153
config.vm.network "forwarded_port", guest: 8154, host: 8154
```

One for `http`, another for `https` -- this will make it possible to use it from https://localhost:8154/go/ url.
After that run
.. code-block:: bash

    vagrant up

and wait some time for machine to load and service to be up.
