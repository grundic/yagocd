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

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import job


class BaseTestJobManager(AbstractTestManager):
    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    def _execute_test_action(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def manager(self, session_fixture):
        return job.JobManager(session=session_fixture)


class TestScheduled(BaseTestJobManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("job/scheduled") as cass:
            return cass, manager.scheduled()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/jobs/scheduled.xml'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/xml'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestHistory(BaseTestJobManager, ReturnValueMixin):
    PIPELINE_NAME = 'Shared_Services'
    STAGE_NAME = 'Commit'
    JOB_NAME = 'build'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("job/history") as cass:
            return cass, manager.history(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                job_name=self.JOB_NAME
            )

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/jobs/{0}/{1}/{2}/history/{3}'.format(
            self.PIPELINE_NAME, self.STAGE_NAME, self.JOB_NAME, 0
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/xml'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(i, job.JobInstance) for i in result)

        return check_value
