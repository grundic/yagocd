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

from yagocd.resources import pipeline
from yagocd.resources import Base
import mock
import pytest


class TestPipelineEntity(object):
    @pytest.fixture()
    def pipeline_entity(self, mock_session):
        return pipeline.PipelineEntity(
            session=mock_session,
            data={'name': 'pipeline_1',
                  'materials': [
                      {'description': 'child_name_1', 'type': 'Pipeline'},
                      {'description': 'git_repo_1', 'type': 'Git'},
                      {'description': 'child_name_2', 'type': 'Pipeline'},
                  ]
                  },
            group='baz'
        )

    def test_entity_is_not_none(self, pipeline_entity):
        assert pipeline_entity is not None

    def test_is_instance_of_base(self, pipeline_entity):
        assert isinstance(pipeline_entity, Base)

    def test_reading_group(self, pipeline_entity):
        assert pipeline_entity.group == 'baz'

    def test_predecessors_empty(self, pipeline_entity):
        assert pipeline_entity.predecessors == list()

    def test_descendants_empty(self, pipeline_entity):
        assert pipeline_entity.descendants == list()

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_call(self, history_mock, pipeline_entity):
        pipeline_entity.history()
        history_mock.assert_called_with(name=pipeline_entity.data.name, offset=0)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.status')
    def test_status_call(self, status_mock, pipeline_entity):
        pipeline_entity.status()
        status_mock.assert_called_with(name=pipeline_entity.data.name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.pause')
    def test_pause_call(self, pause_mock, pipeline_entity):
        pipeline_entity.pause('custom-reason')
        pause_mock.assert_called_with(name=pipeline_entity.data.name, cause='custom-reason')

    @mock.patch('yagocd.resources.pipeline.PipelineManager.unpause')
    def test_unpause_call(self, unpause_mock, pipeline_entity):
        pipeline_entity.unpause()
        unpause_mock.assert_called_with(name=pipeline_entity.data.name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.release_lock')
    def test_release_lock_call(self, release_lock_mock, pipeline_entity):
        pipeline_entity.release_lock()
        release_lock_mock.assert_called_with(name=pipeline_entity.data.name)
