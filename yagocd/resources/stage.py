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

from yagocd.resources.job import JobInstance
from yagocd.resources import BaseManager, Base


class StageManager(BaseManager):
    """
    The stages API allows users to view stage information and operate on it.
    """

    def __init__(
        self,
        session,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
    ):
        super(StageManager, self).__init__(session)

        self._pipeline_name = pipeline_name
        self._pipeline_counter = pipeline_counter
        self._stage_name = stage_name
        self._stage_counter = stage_counter

    def cancel(self, pipeline_name=None, stage_name=None):
        """
        Cancel an active stage of a specified stage.

        :param pipeline_name: pipeline name.
        :param stage_name: stage name.
        :return: a text confirmation.
        """
        assert self._pipeline_name or pipeline_name
        assert self._stage_name or stage_name

        response = self._session.post(
            path='{base_api}/stages/{pipeline_name}/{stage_name}/cancel'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                stage_name=self._stage_name or stage_name
            ),
            headers={'Accept': 'application/json'},
        )
        return response.text

    def get(
        self,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None
    ):
        """
        Gets stage instance object.

        :param pipeline_name: pipeline name.
        :param stage_name: stage name.
        :param pipeline_counter: pipeline counter.
        :param stage_counter: stage counter.
        :return: a stage instance object :class:`yagocd.resources.stage.StageInstance`.
        :rtype: yagocd.resources.stage.StageInstance
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter

        response = self._session.get(
            path='{base_api}/stages/{pipeline_name}/{stage_name}/instance/{pipeline_counter}/{stage_counter}'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter
            ),
            headers={'Accept': 'application/json'},
        )

        return StageInstance(session=self._session, data=response.json(), pipeline=None)

    def history(self, pipeline_name=None, stage_name=None, offset=0):
        """
        The stage history allows users to list stage instances of specified stage.
        Supports pagination using offset which tells the API how many instances to skip.

        :param pipeline_name: pipeline name.
        :param stage_name: stage name.
        :param offset: how many instances to skip.
        :return: an array of stage instances :class:`yagocd.resources.stage.StageInstance`.
        :rtype: list of yagocd.resources.stage.StageInstance
        """
        assert self._pipeline_name or pipeline_name
        assert self._stage_name or stage_name

        response = self._session.get(
            path='{base_api}/stages/{pipeline_name}/{stage_name}/history/{offset}'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                stage_name=self._stage_name or stage_name,
                offset=offset,
            ),
            headers={'Accept': 'application/json'},
        )

        instances = list()
        for instance in response.json().get('stages'):
            instances.append(StageInstance(session=self._session, data=instance, pipeline=None))

        return instances

    def full_history(self, pipeline_name=None, stage_name=None):
        """
        The stage history allows users to list stage instances of specified stage.

        This method uses generator to get full stage history.
        :param pipeline_name: pipeline name.
        :param stage_name: stage name.
        :return: an array of stage instances :class:`yagocd.resources.stage.StageInstance`.
        :rtype: list of yagocd.resources.stage.StageInstance
        """
        offset = 0
        instances = self.history(pipeline_name, stage_name, offset)
        while instances:
            for instance in instances:
                yield instance

            offset += len(instances)
            instances = self.history(pipeline_name, stage_name, offset)


class StageInstance(Base):
    """
    Class representing instance of specific stage.
    """

    def __init__(self, session, data, pipeline):
        super(StageInstance, self).__init__(session, data)
        self._pipeline = pipeline

        self._manager = StageManager(session=self._session)

    @property
    def url(self):
        """
        Returns url for accessing stage instance.
        """
        return "{server_url}/go/pipelines/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}".format(
            server_url=self._session.server_url,
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.data.name,
            stage_counter=self.data.counter,
        )

    @property
    def pipeline_name(self):
        """
        Get pipeline name of current stage instance.

        Because instantiating stage instance could be performed in different ways and those return different results,
        we have to check where from to get name of the pipeline.

        :return: pipeline name.
        """
        if 'pipeline_name' in self.data:
            return self.data.get('pipeline_name')
        elif self.pipeline is not None:
            return self.pipeline.data.name

    @property
    def pipeline_counter(self):
        """
        Get pipeline counter of current stage instance.

        Because instantiating stage instance could be performed in different ways and those return different results,
        we have to check where from to get counter of the pipeline.

        :return: pipeline counter.
        """
        if 'pipeline_counter' in self.data:
            return self.data.get('pipeline_counter')
        elif self.pipeline is not None:
            return self.pipeline.data.counter

    @property
    def stage_name(self):
        """
        Get stage name of current instance.

        This method is to be inline with others.

        :return: stage name.
        """
        if 'name' in self.data:
            return self.data.get('name')

    @property
    def stage_counter(self):
        """
        Get stage counter of current instance.

        This method is to be inline with others.

        :return: stage counter.
        """
        if 'counter' in self.data:
            return self.data.get('counter')

    @property
    def pipeline(self):
        return self._pipeline

    def cancel(self):
        """
        Cancel an active stage of a specified stage.

        :return: a text confirmation.
        """
        return self._manager.cancel(pipeline_name=self.pipeline_name, stage_name=self.stage_name)

    def jobs(self):
        """
        Method for getting jobs from stage instance.

        :return: arrays of jobs.
        :rtype: list of yagocd.resources.job.JobInstance
        """
        jobs = list()
        for data in self.data.jobs:
            jobs.append(JobInstance(session=self._session, data=data, stage=self))

        return jobs
