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
from yagocd.resources import feed


class BaseTestConfigurationManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return feed.FeedManager(session=session)


class TestPipelines(BaseTestConfigurationManager):
    def test_pipelines_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipelines") as cass:
            manager.pipelines()
            assert cass.requests[0].path == '/go/api/pipelines.xml'

    def test_pipelines_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipelines") as cass:
            manager.pipelines()
            assert cass.requests[0].method == 'GET'

    def test_pipelines_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipelines") as cass:
            manager.pipelines()
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_pipelines_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipelines") as cass:
            manager.pipelines()
            assert cass.responses[0]['status']['code'] == 200

    def test_pipelines_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipelines"):
            result = manager.pipelines()
            assert isinstance(result, string_types)


class TestPipelineById(BaseTestConfigurationManager):
    PIPELINE_ID = 3

    def test_pipeline_by_id_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipeline_by_id") as cass:
            manager.pipeline_by_id(self.PIPELINE_ID)
            assert cass.requests[0].path == '/go/api/pipelines/THIS_PARAMETER_IS_USELESS/3.xml'

    def test_pipeline_by_id_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipeline_by_id") as cass:
            manager.pipeline_by_id(self.PIPELINE_ID)
            assert cass.requests[0].method == 'GET'

    def test_pipeline_by_id_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipeline_by_id") as cass:
            manager.pipeline_by_id(self.PIPELINE_ID)
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_pipeline_by_id_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipeline_by_id") as cass:
            manager.pipeline_by_id(self.PIPELINE_ID)
            assert cass.responses[0]['status']['code'] == 200

    def test_pipeline_by_id_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/pipeline_by_id"):
            result = manager.pipeline_by_id(self.PIPELINE_ID)
            assert isinstance(result, string_types)


class TestStages(BaseTestConfigurationManager):
    PIPELINE_NAME = 'Shared_Services'

    def test_stages_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stages") as cass:
            manager.stages(self.PIPELINE_NAME)
            assert cass.requests[0].path == '/go/api/pipelines/{0}/stages.xml'.format(self.PIPELINE_NAME)

    def test_stages_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stages") as cass:
            manager.stages(self.PIPELINE_NAME)
            assert cass.requests[0].method == 'GET'

    def test_stages_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stages") as cass:
            manager.stages(self.PIPELINE_NAME)
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_stages_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stages") as cass:
            manager.stages(self.PIPELINE_NAME)
            assert cass.responses[0]['status']['code'] == 200

    def test_stages_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stages"):
            result = manager.stages(self.PIPELINE_NAME)
            assert isinstance(result, string_types)


class TestStageById(BaseTestConfigurationManager):
    STAGE_ID = 11

    def test_stage_by_id_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage_by_id") as cass:
            manager.stage_by_id(self.STAGE_ID)
            assert cass.requests[0].path == '/go/api/stages/{0}.xml'.format(self.STAGE_ID)

    def test_stage_by_id_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage_by_id") as cass:
            manager.stage_by_id(self.STAGE_ID)
            assert cass.requests[0].method == 'GET'

    def test_stage_by_id_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage_by_id") as cass:
            manager.stage_by_id(self.STAGE_ID)
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_stage_by_id_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage_by_id") as cass:
            manager.stage_by_id(self.STAGE_ID)
            assert cass.responses[0]['status']['code'] == 200

    def test_stage_by_id_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage_by_id"):
            result = manager.stage_by_id(self.STAGE_ID)
            assert isinstance(result, string_types)


class TestStage(BaseTestConfigurationManager):
    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = '6'
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = 1

    def test_stage_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage") as cass:
            manager.stage(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER
            )
            assert cass.requests[0].path == '/go/pipelines/{0}/{1}/{2}/{3}.xml'.format(
                self.PIPELINE_NAME, self.PIPELINE_COUNTER, self.STAGE_NAME, self.STAGE_COUNTER
            )

    def test_stage_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage") as cass:
            manager.stage(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER
            )
            assert cass.requests[0].method == 'GET'

    def test_stage_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage") as cass:
            manager.stage(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER
            )
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_stage_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage") as cass:
            manager.stage(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER
            )
            # we've been redirected to stage-id url
            assert cass.responses[0]['status']['code'] == 302

    def test_stage_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/stage"):
            result = manager.stage(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER
            )
            assert isinstance(result, string_types)


class TestJobStageById(BaseTestConfigurationManager):
    JOB_ID = 1

    def test_job_by_id_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/job_by_id") as cass:
            manager.job_by_id(self.JOB_ID)
            assert cass.requests[0].path == '/go/api/jobs/{0}.xml'.format(self.JOB_ID)

    def test_job_by_id_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/job_by_id") as cass:
            manager.job_by_id(self.JOB_ID)
            assert cass.requests[0].method == 'GET'

    def test_job_by_id_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/job_by_id") as cass:
            manager.job_by_id(self.JOB_ID)
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_job_by_id_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/job_by_id") as cass:
            manager.job_by_id(self.JOB_ID)
            assert cass.responses[0]['status']['code'] == 200

    def test_job_by_id_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("feed/job_by_id"):
            result = manager.job_by_id(self.JOB_ID)
            assert isinstance(result, string_types)
