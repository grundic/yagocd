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
from yagocd.resources.job import JobInstance


class StageManager(object):
    def __init__(self, session):
        self._session = session
        self.base_api = self._session.base_api()

    def cancel(self, pipeline, stage):
        response = self._session.post(
            path='{base_api}/stages/{pipeline}/{stage}/cancel'.format(
                base_api=self.base_api,
                pipeline=pipeline,
                stage=stage
            ),
            headers={'Accept': 'application/json'},
        )
        return response.text

    def get(self, pipeline, stage, pipeline_counter, stage_counter):
        response = self._session.get(
            path='{base_api}/stages/{pipeline}/{stage}/instance/{pipeline_counter}/{stage_counter}'.format(
                base_api=self.base_api,
                pipeline=pipeline,
                stage=stage,
                pipeline_counter=pipeline_counter,
                stage_counter=stage_counter
            ),
            headers={'Accept': 'application/json'},
        )

        return StageInstance(session=self._session, data=response.json(), pipeline=None)

    def history(self, pipeline, stage, offset=0):
        response = self._session.get(
            path='{base_api}/stages/{pipeline}/{stage}/history/{offset}'.format(
                base_api=self.base_api,
                pipeline=pipeline,
                stage=stage,
                offset=offset,
            ),
            headers={'Accept': 'application/json'},
        )

        instances = list()
        for instance in response.json().get('stages'):
            instances.append(StageInstance(session=self._session, data=instance, pipeline=None))

        return instances


class StageInstance(Base):
    def __init__(self, session, data, pipeline):
        super(StageInstance, self).__init__(session, data)
        self._pipeline = pipeline

    @property
    def pipeline(self):
        return self._pipeline

    def jobs(self):
        jobs = list()
        for data in self.data.jobs:
            jobs.append(JobInstance(session=self._session, data=data, stage=self))

        return jobs


if __name__ == '__main__':
    pass
