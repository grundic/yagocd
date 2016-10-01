|gocd_logo| Yet another GoCD python client
==========================================

    .. image:: https://travis-ci.org/grundic/yagocd.svg?branch=master
       :target: https://travis-ci.org/grundic/yagocd

    .. image:: https://coveralls.io/repos/github/grundic/yagocd/badge.svg?branch=master
       :target: https://coveralls.io/github/grundic/yagocd?branch=master

    .. image:: https://badge.fury.io/py/yagocd.svg
       :target: https://badge.fury.io/py/yagocd

    .. image:: https://readthedocs.org/projects/yagocd/badge/?version=latest
       :target: http://yagocd.readthedocs.io

Introduction
------------
This library is a high level python API wrapper upon ThoughtWorks GoCD REST API.
From the official documentation:

    Go Continuous Delivery is continuous integration/deployment server,
    which helps you automate and streamline the build-test-release cycle for worry-free.

Using it, you can access to internals of the Pipelines, check their statuses, download Artifacts and more.
It is designed with maximum comfort and productivity from the user perspective, so it should be very easy
to use it in your own project.
More information is available at official `documentation <http://yagocd.readthedocs.io>`_

Installation
------------
.. code-block:: bash

    $ pip install yagocd

Quick example
-------------

.. code-block:: python

    from yagocd import Yagocd

    go = Yagocd(
        server='https://example.com',
        auth=('user', 'password'),
        options={
            'verify': False  # skip verification for SSL certificates.
        }
    )

    for pipeline in go.pipelines:
        for instance in pipeline:
            for stage in instance:
                for job in stage:
                    # print artifact urls for each job
                    for artifact in job.artifacts:
                        for file_obj in artifact.files():
                            print(file_obj.data.url)

                    # print property of each job
                    for key, value in job.properties.items():
                        print "{} => {}".format(key, value)

Different implementations of GoCD API
-------------------------------------
Here is list of similar projects, that implements GoCD API:

- `py-gocd [python] <https://github.com/gaqzi/py-gocd/>`_: A Python API for interacting with Go Continuous Delivery
- `gocdapi [python] <https://github.com/joaogbcravo/gocdapi>`_: A Python API for accessing resources and configuring Go (thoughtworks) continuous-delivery servers
- `gomatic [python] <https://github.com/SpringerSBM/gomatic>`_: A Python API for configuring GoCD
- `goapi [ruby] <https://github.com/ThoughtWorksStudios/goapi>`_: Go (http://www.go.cd) API ruby client
- `gocd-api [NodeJS] <https://github.com/birgitta410/gocd-api>`_: Access http://www.go.cd API via nodeJS
- `gocd-api [GoLang] <https://github.com/christer79/gocd-api>`_: An implementation of the gocd API

Licence
-------
`MIT <https://raw.githubusercontent.com/grundic/yagocd/master/LICENSE>`_

.. |gocd_logo| image:: https://raw.githubusercontent.com/grundic/yagocd/master/img/gocd_logo.png
