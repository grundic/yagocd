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

from yagocd.resources import artifact, job, pipeline, property as prop, stage


class TestJobInstance(object):
    PIPELINE_NAME = 'Consumer_Website'
    PIPELINE_COUNTER = 31
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'
    JOB_NAME = 'build'
    URL = '{server}go/tab/build/detail/Consumer_Website/31/Commit/1/build'

    @pytest.fixture()
    def job_instance_from_pipeline(self, my_vcr, session_fixture):
        with my_vcr.use_cassette("job/job_instance_from_pipeline"):
            return pipeline.PipelineManager(session_fixture).find(self.PIPELINE_NAME).history()[0].stages()[0].jobs()[0]

    @pytest.fixture()
    def job_instance_from_stage(self, my_vcr, session_fixture):
        with my_vcr.use_cassette("job/job_instance_from_stage"):
            return stage.StageManager(session_fixture).get(
                self.PIPELINE_NAME,
                self.PIPELINE_COUNTER,
                self.STAGE_NAME,
                self.STAGE_COUNTER
            ).jobs()[0]

    @pytest.fixture()
    def job_instance_from_job_manager(self, my_vcr, session_fixture):
        with my_vcr.use_cassette("job/job_instance_from_job_manager"):
            return job.JobManager(session_fixture).history(self.PIPELINE_NAME, self.STAGE_NAME, self.JOB_NAME)[0]

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_pipeline_name(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.pipeline_name == self.PIPELINE_NAME, "Fixture: {}".format(job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_pipeline_counter(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.pipeline_counter == self.PIPELINE_COUNTER, "Fixture: {}".format(job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_stage_name(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.stage_name == self.STAGE_NAME, "Fixture: {}".format(job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_stage_counter(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert str(job_fixture.stage_counter) == self.STAGE_COUNTER, "Fixture: {}".format(job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_url(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.url == self.URL.format(server=job_fixture._session._options['server']), "Fixture: {}".format(
            job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
    ])
    def test_stage_provided(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.stage is not None, "Fixture: {}".format(job_fixture_func.__name__)
        assert isinstance(job_fixture.stage, stage.StageInstance), "Fixture: {}".format(job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_job_manager,
    ])
    def test_stage_is_empty(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.stage is None, "Fixture: {}".format(job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_artifact(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.artifacts is not None, "Fixture: {}".format(job_fixture_func.__name__)
        assert isinstance(job_fixture.artifacts, artifact.ArtifactManager), "Fixture: {}".format(
            job_fixture_func.__name__)

    @pytest.mark.parametrize("job_fixture_func", [
        job_instance_from_pipeline,
        job_instance_from_stage,
        job_instance_from_job_manager,
    ])
    def test_property(self, job_fixture_func, my_vcr, session_fixture):
        job_fixture = job_fixture_func(self, my_vcr, session_fixture)
        assert job_fixture.properties is not None, "Fixture: {}".format(job_fixture_func.__name__)
        assert isinstance(job_fixture.properties, prop.PropertyManager), "Fixture: {}".format(job_fixture_func.__name__)
