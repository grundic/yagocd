#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# The MIT License
#
# Copyright (c) 2016 Grigory Chernyshev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
import json
import time

from easydict import EasyDict

from yagocd.resources import BaseManager, BaseNode
from yagocd.resources.material import ModificationEntity
from yagocd.resources.pipeline_config import PipelineConfigManager
from yagocd.resources.stage import StageInstance
from yagocd.util import since, YagocdUtil


@since('14.3.0')
class PipelineManager(BaseManager):
    """
    The pipelines API allows users to view pipeline information and operate on it.

    `Official documentation. <https://api.go.cd/current/#pipelines>`_

    `Pipeline groups documentation. <https://api.go.cd/current/#pipeline-groups>`_

    :versionadded: 14.3.0.
    """

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :return: array of pipelines
        :rtype: list of yagocd.resources.pipeline.PipelineEntity
        """
        return iter(self.list())

    def __getitem__(self, name):
        """
        Method add possibility to get pipeline by the name using dictionary like syntax.

        :param name: name of the pipeline
        :return: if found - pipeline :class:`yagocd.resources.pipeline.PipelineEntity`, otherwise ``None``.
        :rtype: yagocd.resources.pipeline.PipelineEntity
        """
        return self.find(name=name)

    @since('14.3.0')
    def list(self):
        """
        List all available pipelines.

        :versionadded: 14.3.0.

        This method uses ``pipeline_groups`` API method call to list available pipelines.
        It also links them together, so later it's possible to refer to pipeline's descendants.
        :return: array of pipelines
        :rtype: list of yagocd.resources.pipeline.PipelineEntity
        """
        response = self._session.get(
            path='{base_api}/config/pipeline_groups'.format(base_api=self.base_api),
            headers={'Accept': 'application/json'},
        )

        pipelines = list()
        for group in response.json():
            for data in group['pipelines']:
                pipeline = PipelineEntity(
                    session=self._session,
                    data=data,
                    group=group['name']
                )
                pipelines.append(pipeline)

        # build pipeline graph to link related nodes
        return YagocdUtil.build_graph(
            nodes=pipelines,
            dependencies=lambda parent: [material for material in parent.data.materials],
            compare=lambda candidate, child: candidate.description == child.data.name
        )

    def find(self, name):
        """
        Finds pipeline by it's name.

        :versionadded: 14.3.0.

        :param name: name of required pipeline.
        :return: if found - pipeline :class:`yagocd.resources.pipeline.PipelineEntity`, otherwise ``None``.
        :rtype: yagocd.resources.pipeline.PipelineEntity
        """
        for pipeline in self.list():
            if pipeline.data.name == name:
                return pipeline

    def history(self, name, offset=0):
        """
        The pipeline history allows users to list pipeline instances.
        Supports pagination using offset which tells the API how many instances to skip.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :param offset: number of pipeline instances to be skipped.
        :return: an array of pipeline instances :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: list of yagocd.resources.pipeline.PipelineInstance
        """
        response = self._session.get(
            path='{base_api}/pipelines/{name}/history/{offset}'.format(
                base_api=self.base_api,
                name=name,
                offset=offset
            ),
            headers={'Accept': 'application/json'},
        )

        instances = list()
        for instance in response.json().get('pipelines'):
            instances.append(PipelineInstance(session=self._session, data=instance))

        return instances

    def full_history(self, name):
        """
        Method for accessing full history of specific pipeline.

        :versionadded: 14.3.0.

        It yields each instance and after one chunk is over moves to the next one.
        :param name: name of the pipeline.
        :return: an array of pipeline instances :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: list of yagocd.resources.pipeline.PipelineInstance
        """
        offset = 0
        instances = self.history(name, offset)
        while instances:
            for instance in instances:
                yield instance

            offset += len(instances)
            instances = self.history(name, offset)

    def last(self, name):
        """
        Get last pipeline instance.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        pipeline_history = self.history(name=name)
        if pipeline_history:
            return pipeline_history[0]

    def get(self, name, counter):
        """
        Gets pipeline instance object.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :param counter: pipeline counter.
        :return: A pipeline instance object :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        response = self._session.get(
            path='{base_api}/pipelines/{name}/instance/{counter}'.format(
                base_api=self.base_api,
                name=name,
                counter=counter
            ),
            headers={'Accept': 'application/json'},
        )

        return PipelineInstance(session=self._session, data=response.json())

    def status(self, name):
        """
        The pipeline status allows users to check if the pipeline is paused, locked and schedulable.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :return: JSON containing information about pipeline state, wrapped in EasyDict class.
        """
        response = self._session.get(
            path='{base_api}/pipelines/{name}/status'.format(
                base_api=self.base_api,
                name=name,
            ),
            headers={'Accept': 'application/json'},
        )

        return EasyDict(response.json())

    def pause(self, name, cause):
        """
        Pause the specified pipeline.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :param cause: reason for pausing the pipeline.
        """
        self._session.post(
            path='{base_api}/pipelines/{name}/pause'.format(
                base_api=self.base_api,
                name=name,
            ),
            data={'pauseCause': cause},
            headers={
                'Accept': 'application/json',
                'Confirm': 'true'
            },
        )

    def unpause(self, name):
        """
        Unpause the specified pipeline.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        """
        self._session.post(
            path='{base_api}/pipelines/{name}/unpause'.format(
                base_api=self.base_api,
                name=name,
            ),
            headers={
                'Accept': 'application/json',
                'Confirm': 'true'
            },
        )

    def release_lock(self, name):
        """
        Release a lock on a pipeline so that you can start up a new instance
        without having to wait for the earlier instance to finish.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :return: a text confirmation.
        """
        response = self._session.post(
            path='{base_api}/pipelines/{name}/releaseLock'.format(
                base_api=self.base_api,
                name=name,
            ),
            headers={
                'Accept': 'application/json',
                'Confirm': 'true'
            },
        )
        return response.text

    def schedule(self, name, materials=None, variables=None, secure_variables=None):
        """
        Scheduling allows user to trigger a specific pipeline.

        :versionadded: 14.3.0.

        :param name: name of the pipeline.
        :param materials: material revisions to use.
        :param variables: environment variables to set.
        :param secure_variables: secure environment variables to set.
        :return: a text confirmation.
        """

        data = {'materials': materials, 'variables': variables, 'secure_variables': secure_variables}
        data = dict((k, v) for k, v in data.items() if v is not None)

        response = self._session.post(
            path='{base_api}/pipelines/{name}/schedule'.format(
                base_api=self.base_api,
                name=name,
            ),
            data=json.dumps(data),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Confirm': 'true'
            },
        )

        return response.text

    def schedule_with_instance(
        self,
        name,
        materials=None,
        variables=None,
        secure_variables=None,
        backoff=0.5,
        max_tries=20
    ):
        """
        Schedule pipeline and return instance.
        Credits of implementation comes to `gaqzi`:
        https://github.com/gaqzi/py-gocd/blob/master/gocd/api/pipeline.py#L122

        :versionadded: 14.3.0.

        :warning: Replace this with whatever is the official way as soon as gocd#990 is fixed. \
        https://github.com/gocd/gocd/issues/990

        :param name: name of the pipeline.
        :param materials: material revisions to use.
        :param variables: environment variables to set.
        :param secure_variables: secure environment variables to set.
        :param backoff: time to wait before checking for new instance.
        :param max_tries: maximum tries to do.
        :return: possible triggered instance of pipeline.
        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        last_instance = self.last(name)
        if last_instance:
            last_run_counter = last_instance.data.counter
        else:
            last_run_counter = -1

        self.schedule(name=name, materials=materials, variables=variables, secure_variables=secure_variables)

        while max_tries > 0:
            candidate_instance = self.last(name)
            if candidate_instance and candidate_instance.data.counter > last_run_counter:
                return candidate_instance

            time.sleep(backoff)
            max_tries -= 1

    def value_stream_map(self, name, counter):
        """
        Method builds pipeline instance dependency graph.

        :param name: name of the pipeline.
        :param counter: pipeline counter.
        """
        response = self._session.get(
            path='{base_api}/pipelines/value_stream_map/{name}/{counter}.json'.format(
                base_api=self._session.base_api(api_path=''),
                name=name,
                counter=counter
            ),
            headers={'Accept': 'application/json'},
        )

        data = EasyDict(response.json())

        nodes = list()
        dependencies = dict()

        for level in data['levels']:
            for node_item in level.nodes:
                dependencies[node_item.id] = node_item.parents

                if node_item.node_type == 'PIPELINE':
                    for instance in node_item.instances:
                        pipeline_data = dict(
                            id=node_item.id,
                            name=node_item.name,
                            counter=instance.counter,
                            label=instance.label,
                            type=node_item.node_type.capitalize(),
                            stages=[]
                        )

                        for stage in instance.stages:
                            stage_data = dict(
                                pipeline_name=node_item.name,
                                pipeline_counter=instance.counter,
                                name=stage.name,
                                status=stage.status
                            )
                            pipeline_data['stages'].append(stage_data)

                        nodes.append(PipelineInstance(session=self._session, data=pipeline_data))
                elif node_item.node_type in ['GIT', 'MERCURIAL', 'SUBVERSION']:
                    for instance in node_item.instances:
                        instance['id'] = node_item.id
                        instance['type'] = node_item.node_type.capitalize()
                        nodes.append(ModificationEntity(session=self._session, data=instance))
                elif node_item.node_type == 'DUMMY':  # WTF?!
                    continue
                else:
                    raise RuntimeError('Unknown node type "{}"!'.format(node_item))

        return YagocdUtil.build_graph(
            nodes=nodes,
            dependencies=lambda parent: dependencies[parent.data.id],
            compare=lambda candidate, child: candidate == child.data.id
        )


class PipelineEntity(BaseNode):
    """
    Class for the pipeline entity, which describes pipeline itself.
    Executing ``history`` will return pipeline instances.
    """

    def __init__(self, session, data, group=None):
        super(PipelineEntity, self).__init__(session, data)
        self._group = group
        self._pipeline = PipelineManager(session=session)

    def __iter__(self):
        """
        Method for iterating over all instances of a current pipeline.

        :return: an array of pipeline instances :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: list of yagocd.resources.pipeline.PipelineInstance
        """
        return iter(self.full_history())

    def __getitem__(self, counter):
        """
        Method for accessing to specific pipeline instance in array-like manner.

        :param counter: pipeline counter.
        :return: A pipeline instance object :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        return self.get(counter=counter)

    @property
    def group(self):
        """
        Name of the group pipeline belongs to.
        :return: group name.
        """
        return self._group

    @staticmethod
    def get_url(server_url, pipeline_name):
        """
        Returns url for accessing pipeline entity.
        """
        return "{server_url}/go/tab/pipeline/history/{pipeline_name}".format(
            server_url=server_url,
            pipeline_name=pipeline_name
        )

    @property
    def url(self):
        """
        Returns url for accessing pipeline entity.
        """
        return self.get_url(server_url=self._session.server_url, pipeline_name=self.data.name)

    @property
    def config(self):
        """
        Property for accessing pipeline configuration.

        :rtype: yagocd.resources.pipeline_config.PipelineConfigManager
        """
        return PipelineConfigManager(session=self._session, pipeline_name=self.data.name)

    def history(self, offset=0):
        """
        The pipeline history allows users to list pipeline instances.

        :param offset: number of pipeline instances to be skipped.
        :return: an array of pipeline instances :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: list of yagocd.resources.pipeline.PipelineInstance
        """
        return self._pipeline.history(name=self.data.name, offset=offset)

    def full_history(self):
        """
        Method for accessing full history of specific pipeline.

        It yields each instance and after one chunk is over moves to the next one.
        :return: an array of pipeline instances :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: list of yagocd.resources.pipeline.PipelineInstance
        """
        return self._pipeline.full_history(name=self.data.name)

    def last(self):
        """
        Get last pipeline instance.

        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        return self._pipeline.last(name=self.data.name)

    def get(self, counter):
        """
        Gets pipeline instance object.

        :param counter pipeline counter:
        :return: A pipeline instance object :class:`yagocd.resources.pipeline.PipelineInstance`.
        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        return self._pipeline.get(name=self.data.name, counter=counter)

    def status(self):
        """
        The pipeline status allows users to check if the pipeline is paused, locked and schedulable.

        :return: JSON containing information about pipeline state, wrapped in EasyDict class.
        """
        return self._pipeline.status(name=self.data.name)

    def pause(self, cause):
        """
        Pause the current pipeline.

        :param cause: reason for pausing the pipeline.
        """
        self._pipeline.pause(name=self.data.name, cause=cause)

    def unpause(self):
        """
        Unpause the specified pipeline.
        """
        self._pipeline.unpause(name=self.data.name)

    def release_lock(self):
        """
        Release a lock on a pipeline so that you can start up a new instance
        without having to wait for the earlier instance to finish.

        :return: a text confirmation.
        """
        return self._pipeline.release_lock(name=self.data.name)

    def schedule(self, materials=None, variables=None, secure_variables=None):
        """
        Scheduling allows user to trigger a specific pipeline.

        :param materials: material revisions to use.
        :param variables: environment variables to set.
        :param secure_variables: secure environment variables to set.
        :return: a text confirmation.
        """
        return self._pipeline.schedule(
            name=self.data.name,
            materials=materials,
            variables=variables,
            secure_variables=secure_variables
        )

    def schedule_with_instance(
        self,
        materials=None,
        variables=None,
        secure_variables=None,
        backoff=0.5,
        max_tries=20
    ):
        """
        Schedule pipeline and return instance.
        Credits of implementation comes to `gaqzi`:
        https://github.com/gaqzi/py-gocd/blob/master/gocd/api/pipeline.py#L122

        :warning: Replace this with whatever is the official way as soon as gocd#990 is fixed. \
        https://github.com/gocd/gocd/issues/990

        :param materials: material revisions to use.
        :param variables: environment variables to set.
        :param secure_variables: secure environment variables to set.
        :param backoff: time to wait before checking for new instance.
        :param max_tries: maximum tries to do.
        :return: possible triggered instance of pipeline.
        :rtype: yagocd.resources.pipeline.PipelineInstance
        """
        return self._pipeline.schedule_with_instance(
            name=self.data.name,
            materials=materials,
            variables=variables,
            secure_variables=secure_variables,
            backoff=backoff,
            max_tries=max_tries
        )

    def value_stream_map(self, counter):
        return self._pipeline.value_stream_map(name=self.data.name, counter=counter)


class PipelineInstance(BaseNode):
    """
    Pipeline instance represents concrete execution of specific pipeline.
    """

    def __init__(self, session, data):
        super(PipelineInstance, self).__init__(session, data)
        self._manager = PipelineManager(session=session)

    def __iter__(self):
        """
        Method for iterating over stages of a current pipeline instance.

        :return: arrays of stages
        :rtype: list of yagocd.resources.stage.StageInstance
        """
        return iter(self.stages())

    def __getitem__(self, name):
        """
        Method for accessing to specific stage in array-like manner by name.

        :param name: name of the stage to search.
        :return: found stage or None.
        :rtype: yagocd.resources.stage.StageInstance
        """
        return self.stage(name=name)

    @property
    def url(self):
        """
        Returns url for accessing pipeline instance.
        """
        return "{server_url}/go/pipelines/value_stream_map/{pipeline_name}/{pipeline_counter}".format(
            server_url=self._session.server_url,
            pipeline_name=self.data.name,
            pipeline_counter=self.data.counter
        )

    @property
    def pipeline_url(self):
        """
        Returns url for accessing pipeline entity.
        """
        return PipelineEntity.get_url(server_url=self._session.server_url, pipeline_name=self.data.name)

    def stages(self):
        """
        Method for getting stages from pipeline instance.

        :return: arrays of stages
        :rtype: list of yagocd.resources.stage.StageInstance
        """
        stages = list()
        for data in self.data.stages:
            stages.append(StageInstance(session=self._session, data=data, pipeline=self))

        return stages

    def stage(self, name):
        """
        Method for searching specific stage by it's name.

        :param name: name of the stage to search.
        :return: found stage or None.
        :rtype: yagocd.resources.stage.StageInstance
        """
        for stage in self.stages():
            if stage.data.name == name:
                return stage

    def value_stream_map(self):
        return self._manager.value_stream_map(name=self.data.name, counter=self.data.counter)

    @property
    def config(self):
        """
        Property for accessing pipeline configuration.

        :rtype: yagocd.resources.pipeline_config.PipelineConfigManager
        """
        return PipelineConfigManager(session=self._session, pipeline_name=self.data.name)
