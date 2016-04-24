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

from yagocd.client import Yagocd
from yagocd.session import Session
from yagocd.resources import artifact

import pytest


class BaseTestArtifactManager(object):
    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = 7
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'
    JOB_NAME = 'build'

    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return artifact.ArtifactManager(
            session=session,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME
        )


class TestList(BaseTestArtifactManager):
    def test_list_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("artifact/artifact_list") as cass:
            manager.list()
            assert cass.requests[0].path == (
                '/go'
                '/files'
                '/{pipeline_name}'
                '/{pipeline_counter}'
                '/{stage_name}'
                '/{stage_counter}'
                '/{job_name}.json'
            ).format(
                pipeline_name=self.PIPELINE_NAME,
                pipeline_counter=self.PIPELINE_COUNTER,
                stage_name=self.STAGE_NAME,
                stage_counter=self.STAGE_COUNTER,
                job_name=self.JOB_NAME
            )

    def test_list_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("artifact/artifact_list") as cass:
            manager.list()
            assert cass.requests[0].method == 'GET'

    def test_list_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("artifact/artifact_list") as cass:
            manager.list()
            assert cass.requests[0].headers['accept'] == 'application/vnd.go.cd.v1+json'

    def test_list_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("artifact/artifact_list") as cass:
            manager.list()
            assert cass.responses[0]['status']['code'] == 200

    def test_list_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("artifact/artifact_list"):
            result = manager.list()
            assert isinstance(result, list)

    def test_list_returns_instances_of_artifact(self, manager, my_vcr):
        with my_vcr.use_cassette("artifact/artifact_list"):
            result = manager.list()
            assert all(isinstance(i, artifact.Artifact) for i in result)
