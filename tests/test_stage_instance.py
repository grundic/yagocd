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
import re

import mock
import pytest

from yagocd.resources import job, pipeline, stage


class TestStageInstance(object):
    @pytest.fixture()
    def stage_instance_from_pipeline(self, my_vcr, session_fixture):
        with my_vcr.use_cassette("stage/stage_instance_from_pipeline"):
            return pipeline.PipelineManager(session_fixture).find('Consumer_Website').history()[0].stages()[0]

    @pytest.fixture()
    def stage_instance_from_stage_history(self, my_vcr, session_fixture):
        with my_vcr.use_cassette("stage/stage_instance_from_stage_history"):
            return stage.StageManager(session_fixture).history('Consumer_Website', 'Commit')[0]

    @mock.patch('yagocd.resources.stage.StageInstance.job')
    def test_indexed_based_access(self, job_mock, stage_instance_from_pipeline):
        name = mock.MagicMock()
        _ = stage_instance_from_pipeline[name]  # noqa
        job_mock.assert_called_once_with(name=name)

    @mock.patch('yagocd.resources.stage.StageInstance.jobs')
    def test_iterator_access(self, jobs_mock, stage_instance_from_pipeline):
        for _ in stage_instance_from_pipeline:
            pass
        jobs_mock.assert_called_once_with()

    def test_url_from_pipeline(self, stage_instance_from_pipeline):
        url_re = re.compile('{server}go/pipelines/Consumer_Website/\d+/Commit/\d+'.format(
            server=stage_instance_from_pipeline._session._options['server']
        ))

        assert url_re.match(stage_instance_from_pipeline.url)

    def test_url_from_history(self, stage_instance_from_stage_history):
        url_re = re.compile(r'{server}go/pipelines/Consumer_Website/\d+/Commit/\d+'.format(
            server=stage_instance_from_stage_history._session._options['server']
        ))

        assert url_re.match(stage_instance_from_stage_history.url)

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

    @mock.patch('yagocd.resources.stage.StageInstance.jobs')
    def test_job(self, stages_mock, stage_instance_from_pipeline):
        foo = mock.MagicMock()
        foo.data.name = 'foo'
        bar = mock.MagicMock()
        bar.data.name = 'bar'
        baz = mock.MagicMock()
        baz.data.name = 'baz'
        stages_mock.return_value = [foo, bar, baz]

        result = stage_instance_from_pipeline.job(name='baz')
        assert result == baz
