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

from yagocd.resources import BaseManager, Base
from yagocd.resources.artifact import ArtifactManager
from yagocd.resources.property import PropertyManager


class JobManager(BaseManager):
    """
    The jobs API allows users to view job information.
    """

    def scheduled(self):
        """
        Lists all the current job instances which are scheduled but not yet assigned to any agent.

        :return: an array of scheduled job instances in XML format.
        """
        response = self._session.get(
            path='{base_api}/jobs/scheduled.xml'.format(base_api=self.base_api),
            headers={'Accept': 'application/xml'},
        )

        return response.text

    def history(self, pipeline_name, stage_name, job_name, offset=0):
        """
        The job history allows users to list job instances of specified job.
        Supports pagination using offset which tells the API how many instances to skip.

        :return: an array of jobs instances.
        """
        response = self._session.get(
            path='{base_api}/jobs/{pipeline_name}/{stage_name}/{job_name}/history/{offset}'.format(
                base_api=self.base_api,
                pipeline_name=pipeline_name,
                stage_name=stage_name,
                job_name=job_name,
                offset=offset
            ),
            headers={'Accept': 'application/xml'},
        )

        instances = list()
        for instance in response.json().get('jobs'):
            instances.append(JobInstance(session=self._session, data=instance, stage=None))

        return instances


class JobInstance(Base):
    """
    Class representing specific job.

    Instances of this class can get different information about the job:
        * get pipeline name/counter
        * get stage name/counter
        * list available artifacts
        * list available properties
    """

    def __init__(self, session, data, stage):
        super(JobInstance, self).__init__(session, data)
        self._stage = stage

    @property
    def pipeline_name(self):
        """
        Get pipeline name of current job instance.

        Because instantiating job instance could be performed in different ways and those return different results,
        we have to check where from to get name of the pipeline.

        :return: pipeline name.
        """
        if 'pipeline_name' in self.data and self.data.pipeline_name:
            return self.data.get('pipeline_name')
        elif self.stage.pipeline is not None:
            return self.stage.pipeline.data.name
        else:
            return self.stage.data.pipeline_name

    @property
    def pipeline_counter(self):
        """
        Get pipeline counter of current job instance.

        Because instantiating job instance could be performed in different ways and those return different results,
        we have to check where from to get counter of the pipeline.

        :return: pipeline counter.
        """
        if 'pipeline_counter' in self.data and self.data.pipeline_counter:
            return self.data.get('pipeline_counter')
        elif self.stage.pipeline is not None:
            return self.stage.pipeline.data.counter
        else:
            return self.stage.data.pipeline_counter

    @property
    def stage_name(self):
        """
        Get stage name of current job instance.

        Because instantiating job instance could be performed in different ways and those return different results,
        we have to check where from to get name of the stage.

        :return: stage name.
        """
        if 'stage_name' in self.data and self.data.stage_name:
            return self.data.get('stage_name')
        else:
            return self.stage.data.name

    @property
    def stage_counter(self):
        """
        Get stage counter of current job instance.

        Because instantiating job instance could be performed in different ways and those return different results,
        we have to check where from to get counter of the stage.

        :return: stage counter.
        """
        if 'stage_counter' in self.data and self.data.stage_counter:
            return self.data.get('stage_counter')
        else:
            return self.stage.data.counter

    @property
    def url(self):
        """
        Returns url for accessing job instance.
        """
        return (
            "{server_url}/go/tab/build/detail"
            "/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}").format(
            server_url=self._session.server_url,
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.stage_name,
            stage_counter=self.stage_counter,
            job_name=self.data.name
        )

    @property
    def stage(self):
        return self._stage

    @property
    def artifact(self):
        """
        Property for accessing artifact manager of the current job.

        :return: instance of :class:`yagocd.resources.artifact.ArtifactManager`
        :rtype: yagocd.resources.artifact.ArtifactManager
        """
        return ArtifactManager(
            session=self._session,
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.stage_name,
            stage_counter=self.stage_counter,
            job_name=self.data.name
        )

    @property
    def prop(self):
        """
        Property for accessing property (doh!) manager of the current job.

        :return: instance of :class:`yagocd.resources.property.PropertyManager`
        :rtype: yagocd.resources.property.PropertyManager
        """
        return PropertyManager(
            session=self._session,
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.stage_name,
            stage_counter=self.stage_counter,
            job_name=self.data.name
        )
