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
from yagocd.resources import pipeline, stage, job
from yagocd.session import Session

import mock
import pytest


class TestStageInstance(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def stage_instance_from_pipeline(self, my_vcr, session):
        with my_vcr.use_cassette("stage/stage_instance_from_pipeline"):
            return pipeline.PipelineManager(session).find('Consumer_Website').history()[0].stages()[0]

    @pytest.fixture()
    def stage_instance_from_stage_history(self, my_vcr, session):
        with my_vcr.use_cassette("stage/stage_instance_from_stage_history"):
            return stage.StageManager(session).history('Consumer_Website', 'Commit')[0]

    def test_has_all_managers_methods(self):
        excludes = ['get', 'history', 'full_history']

        def get_public_methods(klass):
            methods = set()
            for name in dir(klass):
                if name.startswith('_'):
                    continue

                candidate = getattr(klass, name)
                if hasattr(candidate, '__call__'):
                    methods.add(name)
            return methods

        managers_methods = get_public_methods(stage.StageManager)
        entity_methods = get_public_methods(stage.StageInstance)
        result = managers_methods - entity_methods - set(excludes)
        assert len(result) == 0, "Some methods are missing in pipeline entity: {}".format(result)

    def test_url_from_pipeline(self, stage_instance_from_pipeline):
        assert stage_instance_from_pipeline.url == 'http://localhost:8153/go/pipelines/Consumer_Website/29/Commit/1'

    def test_url_from_history(self, stage_instance_from_stage_history):
        assert stage_instance_from_stage_history.url == 'http://localhost:8153/go/pipelines/Consumer_Website/29/Commit/1'

    def test_pipeline_is_not_none(self, stage_instance_from_pipeline):
        assert stage_instance_from_pipeline.pipeline is not None

    def test_pipeline_is_none(self, stage_instance_from_stage_history):
        assert stage_instance_from_stage_history.pipeline is None

    def test_stage_counter_from_pipeline(self, stage_instance_from_pipeline):
        assert stage_instance_from_pipeline.stage_counter == '1'

    def test_stage_counter_from_stage(self, stage_instance_from_stage_history):
        assert stage_instance_from_stage_history.stage_counter == '1'

    @mock.patch('yagocd.resources.stage.StageManager.cancel')
    def test_cancel_call_from_pipeline(self, cancel_mock, stage_instance_from_pipeline):
        stage_instance_from_pipeline.cancel()
        cancel_mock.assert_called_with(
            pipeline_name=stage_instance_from_pipeline.pipeline_name,
            stage_name=stage_instance_from_pipeline.stage_name
        )

    @mock.patch('yagocd.resources.stage.StageManager.cancel')
    def test_cancel_call_from_stage(self, cancel_mock, stage_instance_from_stage_history):
        stage_instance_from_stage_history.cancel()
        cancel_mock.assert_called_with(
            pipeline_name=stage_instance_from_stage_history.pipeline_name,
            stage_name=stage_instance_from_stage_history.stage_name
        )

    def test_jobs_return_type_from_pipeline(self, stage_instance_from_pipeline):
        jobs = stage_instance_from_pipeline.jobs()
        assert all(isinstance(j, job.JobInstance) for j in jobs)

    def test_jobs_return_type_from_stage(self, stage_instance_from_stage_history):
        jobs = stage_instance_from_stage_history.jobs()
        assert all(isinstance(j, job.JobInstance) for j in jobs)
