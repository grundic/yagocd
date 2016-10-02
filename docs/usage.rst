=====
Usage
=====

Here you can find quick introduction into the usage of different components of the library.
It's far from complete and is not intended to cover all functionality.
To get more information you can address :doc:`modules <modules>` documentation.

Initialization
--------------

To use GoCD Python API client in a project you have to import it first::

  from yagocd import Yagocd

Next, you can create an instance of the client for connecting to the server::

  client = Yagocd(
        server='http://localhost:8153/',
        auth=('admin', 'secret')
    )

Here, we created a client, which would connect to the server running on a localhost, port number `8153`.
Please note, that you don't have to put ``go/`` context path to the ``server`` variable. ``auth`` is a tuple of
login and password for connecting to the server.
There is possibility to set additional parameters during initialization, passing them to the ``options`` variable:

- ``context_path``: server context path to use (default is ``go/``).
- ``verify``: verify SSL certs. Defaults to ``True``.

Managers
++++++++

:class:`Yagocd <yagocd.client.Yagocd>` is the only class that you usually would need to work with, therefore it gives access to all
other resources. Each resource have a manager associated with it. Managers represents a classes with list of public
methods that could be used by client code.
In some cases those methods return some objects that could inspected or used. Majority of those objects are inherited
from :class:`Base <yagocd.resources.Base>` class, which has special ``data`` attribute for accessing to object's data
via dot notation, e.g.::

  pipeline = client.pipelines['Shared_Services']
  print(pipeline.data.name)
  >> Shared_Services

Further you would find examples of using some of those managers.

Pipelines
---------

Pipelines are one of the core components in GoCD architecture.
The pipelines API allows users to view pipeline information and operate on it.

Listing pipelines
+++++++++++++++++

Here how you can get list of them::

  pipelines = client.pipelines.list()

Or you can use iteration instead :func:`list()`::

  for pipeline in client.pipelines:
    print(pipeline)

Beware though, listing all pipelines could be heavy operation in case you have zillions of pipelines of your server.

Getting specific pipeline
+++++++++++++++++++++++++

If you know the name of the pipeline in advance, you can use :func:`get()` or array-like access syntax::

  pipeline = client.pipelines.get('Shared_Services')
  # OR
  pipeline = client.pipelines['Shared_Services']

As there no separate method for getting specific pipeline, current implementation of :func:`get()` is based on filtering
the results of the :func:`list()`.

Pipelines are linked together
+++++++++++++++++++++++++++++

There is an interesting feature when you are working with pipelines through Yagocd library: as pipelines could have
relations between each other, this information is used to build a graph of dependencies between them. You can use this
in your code like this::

  pipeline = client.pipelines.get('Consumer_Website')
  for child in pipeline.predecessors:
    print(child)

  for parent in pipeline.descendants:
    print(parent)

``predecessors`` and ``descendants`` are properties for accessing appropriate relations. By default only direct
relations are fetched. If you need to get all of them, you can use ``get_predecessors(transitive=True)`` and
``get_descendants(transitive=True)`` methods correspondingly.

Getting instance of a pipeline
++++++++++++++++++++++++++++++

First of all, there is a difference between pipeline and pipeline instance: first is a descriptor or configuration
of a pipeline. You can schedule execution of it or get it's history. Pipeline instance is an execution of a given
pipeline. You can check it's logs, for example.

History would give you execution history of a given pipline.
To get pipeline history, i.e. pipeline instances, you can use :func:`history()` or :func:`full_history()`. Latter would
not stop after first 10 items, but would iterate over all executions of a given pipeline.

It's possible to use :func:`last()` method, which would return you the most recent pipeline instance.

Finally, it's possible to get instance of a pipeline by it's counter using :func:`get()` method and passing counter as
a parameter.

Accessing stages of a pipeline instance
+++++++++++++++++++++++++++++++++++++++

As pipeline could have one or more stages, you might want to access this information. You can use :func:`stages()`
method to get list of available stages::

  pipeline = client.pipelines.get('Consumer_Website')
  pipeline_instance = pipeline.last()
  stages = pipeline_instance.stages()
  # OR
  for stage in pipeline_instance:
    print(stage)

If you are interested in specific stage, you can get it by name::

  stage = pipeline_instance['stage_name']

Stages
------

The stages API allows users to view stage information and operate on it.

Accessing jobs of a stage instance
++++++++++++++++++++++++++++++++++

Stage instance gives you access to it's job instances::

  stage_instance = client.stages.get(
    pipeline_name='Consumer_Website',
    pipeline_counter=31,
    stage_name='Commit',
    stage_counter=1
  )

  jobs = stage_instance.jobs()
  # OR
  for job in stage_instance:
    print(job)

If you are interested in specific job, you can get it by name::

  job = stage_instance['job_name']

Jobs
----

The jobs API allows users to view job information.

Accessing artifacts
+++++++++++++++++++

You can list available artifacts for specific job::

  artifacts = job.artifacts.list()
  # OR
  for artifact in job.artifacts:
    print(artifact)

Each artifact could have some files or directories in it. You can iterate over them and get it's content::

  for filename in artifact.files():
    content = filename.fetch()

If you know the name of the file or the directory, you can download it like this::

  file_content = job.artifacts['/path/to/filename.txt']
  dir_zip_content = job.artifacts['/path/to/folder.zip']


Accessing properties
++++++++++++++++++++

Job could have properties set during build. The are represented in dictionary-based form.
You can iterate over them like this::

  for name, value in job.properties.items():
    print(name, value)

Or you can read value of specific property by it's name::

  value = job.properties['property_name']

