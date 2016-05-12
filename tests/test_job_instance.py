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

from yagocd import Yagocd
from yagocd.resources import pipeline, stage, job, artifact, property as prop
from yagocd.session import Session

import mock
import pytest


class TestJobInstance(object):
    PIPELINE_NAME = 'Consumer_Website'
    PIPELINE_COUNTER = 29
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'
    JOB_NAME = 'build'
    URL = 'http://localhost:8153/go/tab/build/detail/Consumer_Website/29/Commit/1/build'

    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def job_instance_from_pipeline(self, my_vcr, session):
        with my_vcr.use_cassette("job/job_instance_from_pipeline"):
            return pipeline.PipelineManager(session).find(self.PIPELINE_NAME).history()[0].stages()[0].jobs()[0]

    @pytest.fixture()
    def job_instance_from_stage(self, my_vcr, session):
        with my_vcr.use_cassette("job/job_instance_from_stage"):
            return stage.StageManager(session).get(
                self.PIPELINE_NAME,
                self.PIPELINE_COUNTER,
                self.STAGE_NAME,
                self.STAGE_COUNTER
            ).jobs()[0]

    @pytest.fixture()
    def job_instance_from_job_manager(self, my_vcr, session):
        with my_vcr.use_cassette("job/job_instance_from_job_manager"):
            return job.JobManager(session).history(self.PIPELINE_NAME, self.STAGE_NAME, self.JOB_NAME)[0]

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_pipeline_name(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.pipeline_name == self.PIPELINE_NAME, "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_pipeline_counter(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.pipeline_counter == self.PIPELINE_COUNTER, "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_stage_name(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.stage_name == self.STAGE_NAME, "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_stage_counter(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert str(job_fixture.stage_counter) == self.STAGE_COUNTER, "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_url(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.url == self.URL, "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
    ])
    def test_stage_provided(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.stage is not None, "Fixture: {}".format(job_fixture_name)
        assert isinstance(job_fixture.stage, stage.StageInstance), "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_job_manager',
    ])
    def test_stage_is_empty(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.stage is None, "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_artifact(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.artifact is not None, "Fixture: {}".format(job_fixture_name)
        assert isinstance(job_fixture.artifact, artifact.ArtifactManager), "Fixture: {}".format(job_fixture_name)

    @pytest.mark.parametrize("job_fixture_name", [
        'job_instance_from_pipeline',
        'job_instance_from_stage',
        'job_instance_from_job_manager',
    ])
    def test_property(self, job_fixture_name, request):
        job_fixture = request.getfuncargvalue(job_fixture_name)
        assert job_fixture.prop is not None, "Fixture: {}".format(job_fixture_name)
        assert isinstance(job_fixture.prop, prop.PropertyManager), "Fixture: {}".format(job_fixture_name)
