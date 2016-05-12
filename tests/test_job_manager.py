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

import pytest
from six import string_types

from yagocd.client import Yagocd
from yagocd.session import Session
from yagocd.resources import job


class BaseTestJobManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return job.JobManager(session=session)


class TestScheduled(BaseTestJobManager):
    def test_scheduled_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("job/scheduled") as cass:
            manager.scheduled()
            assert cass.requests[0].path == '/go/api/jobs/scheduled.xml'

    def test_scheduled_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("job/scheduled") as cass:
            manager.scheduled()
            assert cass.requests[0].method == 'GET'

    def test_scheduled_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("job/scheduled") as cass:
            manager.scheduled()
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_scheduled_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("job/scheduled") as cass:
            manager.scheduled()
            assert cass.responses[0]['status']['code'] == 200

    def test_scheduled_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("job/scheduled"):
            result = manager.scheduled()
            assert isinstance(result, string_types)


class TestHistory(BaseTestJobManager):
    PIPELINE_NAME = 'Shared_Services'
    STAGE_NAME = 'Commit'
    JOB_NAME = 'build'

    def test_history_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("job/history") as cass:
            manager.history(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                job_name=self.JOB_NAME
            )
            assert cass.requests[0].path == '/go/api/jobs/{0}/{1}/{2}/history/{3}'.format(
                self.PIPELINE_NAME, self.STAGE_NAME, self.JOB_NAME, 0
            )

    def test_history_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("job/history") as cass:
            manager.history(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                job_name=self.JOB_NAME
            )
            assert cass.requests[0].method == 'GET'

    def test_history_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("job/history") as cass:
            manager.history(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                job_name=self.JOB_NAME
            )
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_history_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("job/history") as cass:
            manager.history(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                job_name=self.JOB_NAME
            )
            assert cass.responses[0]['status']['code'] == 200

    def test_history_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("job/history"):
            result = manager.history(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                job_name=self.JOB_NAME
            )
            assert all(isinstance(i, job.JobInstance) for i in result)
