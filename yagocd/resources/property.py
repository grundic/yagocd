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

from StringIO import StringIO
import csv

from yagocd.resources import BaseManager


class PropertyManager(BaseManager):
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
        :type session: yagocd.session.Session
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
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.post(
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


if __name__ == '__main__':
    pass
