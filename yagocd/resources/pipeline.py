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

from yagocd.resources.base import Base
from yagocd.resources.stage import StageInstance

from easydict import EasyDict


class PipelineManager(object):
    def __init__(self, client):
        """

        :type client: yagocd.client.Client
        """
        self._client = client
        self.base_api = self._client.base_api()

    @staticmethod
    def tie_descendants(pipelines):
        for pipeline in pipelines:
            descendants = list()

            for descendant in pipelines:
                for material in descendant.data.materials:
                    if material.type == 'Pipeline' and material.description == pipeline.data.name:
                        descendants.append(descendant)
            pipeline.descendants = descendants

    def list(self):
        response = self._client.get(
            path='{base_api}/config/pipeline_groups'.format(base_api=self.base_api),
            headers={'Accept': 'application/json'},
        )

        pipelines = list()
        for group in response.json():
            for data in group['pipelines']:
                pipeline = PipelineEntity(
                    client=self._client,
                    data=data,
                    group=group['name']
                )
                pipelines.append(pipeline)

        # link descendants of each pipeline entity
        self.tie_descendants(pipelines)

        return pipelines

    def find(self, name):
        """
        :rtype: yagocd.resources.PipelineEntity
        """
        for pipeline in self.list():
            if pipeline.data.name == name:
                return pipeline

    def get(self, name, counter):
        response = self._client.get(
            path='{base_api}/pipelines/{name}/instance/{counter}'.format(
                base_api=self.base_api,
                name=name,
                counter=counter
            ),
            headers={'Accept': 'application/json'},
        )

        return PipelineInstance(client=self._client, data=response.json())

    def status(self, name):
        response = self._client.get(
            path='{base_api}/pipelines/{name}/status'.format(
                base_api=self.base_api,
                name=name,
            ),
            headers={'Accept': 'application/json'},
        )

        return EasyDict(response.json())


class PipelineEntity(Base):
    def __init__(self, client, data, group=None, descendants=None):
        super(PipelineEntity, self).__init__(client, data)
        self._group = group
        self._descendants = descendants

    @property
    def group(self):
        return self._group

    @property
    def descendants(self):
        return self._descendants

    @descendants.setter
    def descendants(self, value):
        self._descendants = value

    def history(self, offset=0):
        response = self._client.get(
            path='{base_api}/pipelines/{name}/history/{offset}'.format(
                base_api=self.base_api,
                name=self.data.name,
                offset=offset
            ),
            headers={'Accept': 'application/json'},
        )

        instances = list()
        for instance in response.json().get('pipelines'):
            instances.append(PipelineInstance(client=self._client, data=instance))

        return instances

    def status(self):
        return self._client.pipeline.status(name=self.data.name)


class PipelineInstance(Base):
    def stages(self):
        stages = list()
        for data in self.data.stages:
            stages.append(StageInstance(client=self._client, data=data, pipeline=self))

        return stages


if __name__ == '__main__':
    pass
