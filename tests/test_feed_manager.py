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
from yagocd.resources import feed


class BaseTestConfigurationManager(AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def manager(self, session_fixture):
        return feed.FeedManager(session=session_fixture)

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


class TestPipelines(BaseTestConfigurationManager):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipelines") as cass:
            return cass, manager.pipelines()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines.xml'


class TestPipelineById(BaseTestConfigurationManager):
    PIPELINE_ID = 3

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipeline_by_id") as cass:
            return cass, manager.pipeline_by_id(self.PIPELINE_ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/THIS_PARAMETER_IS_USELESS/3.xml'


class TestStages(BaseTestConfigurationManager):
    PIPELINE_NAME = 'Shared_Services'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stages") as cass:
            return cass, manager.stages(self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{0}/stages.xml'.format(self.PIPELINE_NAME)


class TestStageById(BaseTestConfigurationManager):
    STAGE_ID = 11

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage_by_id") as cass:
            return cass, manager.stage_by_id(self.STAGE_ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/stages/{0}.xml'.format(self.STAGE_ID)


class TestStage(BaseTestConfigurationManager):
    EXPECTED_CASSETTE_COUNT = 2  # because of redirect

    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = '6'
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = 1

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage") as cass:
            return cass, manager.stage(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER
            )

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/pipelines/{0}/{1}/{2}/{3}.xml'.format(
            self.PIPELINE_NAME, self.PIPELINE_COUNTER, self.STAGE_NAME, self.STAGE_COUNTER
        )

    @pytest.fixture()
    def expected_response_code(self, *args, **kwargs):
        return 302  # we've been redirected to stage-id url

    def test_real_response_code(self, _execute_test_action, expected_response_code):
        cass, result = _execute_test_action
        assert cass.responses[1]['status']['code'] == 200


class TestJobStageById(BaseTestConfigurationManager):
    TEST_METHOD_NAME = 'job_by_id'
    JOB_ID = 1

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/job_by_id") as cass:
            return cass, manager.job_by_id(self.JOB_ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/jobs/{0}.xml'.format(self.JOB_ID)
