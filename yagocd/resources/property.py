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

from six import StringIO
import csv

from yagocd.resources import BaseManager


class PropertyManager(BaseManager):
    """
    The properties API allows managing of job properties.
    """

    def __init__(
        self,
        session,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Constructs instance of ``PropertyManager``.
        Parameters to the constructor and methods of the class could be duplicated. That is because of two use cases
        of this class:
            1. When the class being instantiated from :class:`yagocd.client.Client`, we don't know all the necessary
             parameters yet, but we need an instance to work with. So we skip parameters instantiation in constructor,
             but require them for each method.
            2. When the class being used from :class:`yagocd.resources.job.JobInstance` - in this case we already
            know all required parameters, so we can instantiate `PropertyManager` with them.

        :param session: session object from client.
        :type session: yagocd.session.Session.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        """
        super(PropertyManager, self).__init__(session)

        self.base_api = self._session.base_api(api_path='')

        self._pipeline_name = pipeline_name
        self._pipeline_counter = pipeline_counter
        self._stage_name = stage_name
        self._stage_counter = stage_counter
        self._job_name = job_name

    def list(
        self,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Lists all job properties.

        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: dictionary of properties.
        :rtype: dict[str, str]
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.get(
            path='{base_api}/properties/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name
            ),
            headers={'Accept': 'application/json'},
        )
        text = StringIO(response.text)
        parsed = list(csv.reader(text))
        properties = dict(zip(parsed[0], parsed[1]))

        return properties

    def get(
        self,
        name,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Gets a property by its name.
        :info: You can use keyword `latest` as a pipeline counter or a stage counter.

        :param name: name of property to get.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: single property as a dictionary.
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.get(
            path='{base_api}/properties/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}/{name}'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name,
                name=name
            ),
            headers={'Accept': 'application/json'},
        )
        text = StringIO(response.text)
        parsed = list(csv.reader(text))
        properties = dict(zip(parsed[0], parsed[1]))

        return properties

    def historical(self, pipeline_name=None, stage_name=None, job_name=None, limit_pipeline=None, limit_count=None):
        """
        Get historical properties.
        :info: `limitPipeline` and `limitCount` are optional parameters. The default value of
        `limitPipeline` is latest pipeline instance’s counter. The default value of `limitCount` is `100`.

        :param pipeline_name: name of the pipeline.
        :param stage_name: name of the stage.
        :param job_name: name of the job.
        :param limit_pipeline: pipeline limit for returned properties.
        :param limit_count: count limit for returned properties.
        :return: list of dictionaries as historical values.
        """
        assert self._pipeline_name or pipeline_name
        assert self._stage_name or stage_name
        assert self._job_name or job_name

        params = {
            'pipelineName': self._pipeline_name or pipeline_name,
            'stageName': self._stage_name or stage_name,
            'jobName': self._job_name or job_name,
        }
        if limit_pipeline is not None:
            params['limitPipeline'] = limit_pipeline
        if limit_count is not None:
            params['limitCount'] = limit_count

        response = self._session.get(
            path='{base_api}/properties/search'.format(base_api=self.base_api),
            params=params,
            headers={'Accept': 'application/json'},
        )

        text = StringIO(response.text)
        result = list(csv.DictReader(text))

        return result

    def create(
        self,
        name,
        value,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Defines a property on a specific job instance.

        :param name: name of property.
        :param value: value of property.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: an acknowledgement that the property was created.
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.post(
            path='{base_api}/properties/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}/{name}'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name,
                name=name
            ),
            data={'value': value},
            headers={'Accept': 'application/json'},
        )
        return response.text
