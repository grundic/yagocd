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

from unittest import TestCase

from yagocd.resources import pipeline
from yagocd.resources import Base
import mock


class TestPipelineEntity(TestCase):
    def setUp(self):
        self.patcher = mock.patch('yagocd.session.Session')
        self.mock_session = self.patcher.start()

        self.entity = pipeline.PipelineEntity(
            session=self.mock_session,
            data={'name': 'pipeline_1',
                  'materials': [
                      {'description': 'child_name_1', 'type': 'Pipeline'},
                      {'description': 'git_repo_1', 'type': 'Git'},
                      {'description': 'child_name_2', 'type': 'Pipeline'},
                  ]
                  },
            group='baz'
        )

    def test_is_instance_of_base(self):
        self.assertIsInstance(self.entity, Base)

    def test_construction(self):
        self.assertIsNotNone(self.entity)

    def test_reading_group(self):
        self.assertEqual(self.entity.group, 'baz')

    def test_predecessors(self):
        self.assertEqual(
            self.entity.predecessors,
            [
                {'description': 'child_name_1', 'type': 'Pipeline'},
                {'description': 'child_name_2', 'type': 'Pipeline'}
            ]
        )

    def test_descendants_empty(self):
        self.assertIsNone(self.entity.descendants)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_call(self, history_mock):
        self.entity.history()
        history_mock.assert_called_with(name=self.entity.data.name, offset=0)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.status')
    def test_status_call(self, status_mock):
        self.entity.status()
        status_mock.assert_called_with(name=self.entity.data.name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.pause')
    def test_pause_call(self, pause_mock):
        self.entity.pause('custom-reason')
        pause_mock.assert_called_with(name=self.entity.data.name, cause='custom-reason')

    @mock.patch('yagocd.resources.pipeline.PipelineManager.unpause')
    def test_unpause_call(self, unpause_mock):
        self.entity.unpause()
        unpause_mock.assert_called_with(name=self.entity.data.name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.release_lock')
    def test_release_lock_call(self, release_lock_mock):
        self.entity.release_lock()
        release_lock_mock.assert_called_with(name=self.entity.data.name)
