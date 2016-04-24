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

from yagocd.client import Yagocd
from yagocd.session import Session
from yagocd.resources import pipeline

import mock
from vcr import VCR
from requests import HTTPError

my_vcr = VCR(
    cassette_library_dir='tests/fixtures/cassettes',
    path_transformer=VCR.ensure_suffix('.yaml')
)


class TestPipelineManager(TestCase):
    def setUp(self):
        self.session = Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)
        self.manager = pipeline.PipelineManager(session=self.session)

    def test_tie_descendants(self):
        child = pipeline.PipelineEntity(
            session=self.session,
            data={'name': 'child1', 'materials': {}}
        )

        parent = pipeline.PipelineEntity(
            session=self.session,
            data={'name': 'parent1', 'materials': [{'description': 'child1', 'type': 'Pipeline'}]}
        )

        pipelines = [child, parent]

        self.manager.tie_descendants(pipelines)
        self.assertEqual(child.descendants, [parent])

    @my_vcr.use_cassette("pipeline/pipeline_list")
    def test_list_is_not_empty(self):
        result = self.manager.list()
        self.assertTrue(all(isinstance(i, pipeline.PipelineEntity) for i in result))

    @my_vcr.use_cassette("pipeline/pipeline_list")
    def test_elements_in_list_are_pipelines_entities(self):
        result = self.manager.list()
        self.assertTrue(all(isinstance(i, pipeline.PipelineEntity) for i in result))

    @my_vcr.use_cassette("pipeline/pipeline_list")
    @mock.patch('yagocd.resources.pipeline.PipelineManager.tie_descendants')
    def test_tie_descendants_is_called_for_list(self, mock_tie_descendants):
        self.manager.list()
        mock_tie_descendants.assert_called()

    @my_vcr.use_cassette('pipeline/pipeline_list')
    def test_find_non_existing(self):
        result = self.manager.find('This_Pipeline_Doesnt_Exists')
        self.assertIsNone(result)

    @my_vcr.use_cassette('pipeline/pipeline_list')
    def test_find(self):
        name = 'Production_Services'
        result = self.manager.find(name)

        self.assertIsInstance(result, pipeline.PipelineEntity)
        self.assertTrue(result.data.name, name)

    @my_vcr.use_cassette('pipeline/history_non_existing')
    def test_history_non_existing(self):
        self.assertRaises(HTTPError, self.manager.history, "pipeline_non_existing")

    @my_vcr.use_cassette('pipeline/history_Consumer_Website')
    def test_history(self):
        name = "Consumer_Website"
        result = self.manager.history(name)

        self.assertTrue(all(isinstance(i, pipeline.PipelineInstance) for i in result))
        self.assertTrue(all(i.data.name == name for i in result))

    @my_vcr.use_cassette('pipeline/get_non_existing')
    def test_get_non_existing(self):
        self.assertRaises(HTTPError, self.manager.get, "pipeline_instance_non_existing", 1)

    @my_vcr.use_cassette('pipeline/get_Consumer_Website')
    def test_get(self):
        name = "Consumer_Website"
        result = self.manager.get(name, 2)
        self.assertIsInstance(result, pipeline.PipelineInstance)
        self.assertEqual(result.data.name, name)

    @my_vcr.use_cassette('pipeline/status_Consumer_Website')
    def test_status(self):
        name = "Consumer_Website"
        result = self.manager.status(name)
        self.assertDictEqual(
            result,
            {'paused': False, 'schedulable': True, 'locked': False}
        )

    @my_vcr.use_cassette('pipeline/pause_Consumer_Website')
    def test_pause(self):
        name = "Consumer_Website"
        reason = 'Test pause reason'
        self.manager.unpause(name)

        result = self.manager.pause(name, reason)
        self.assertIsNone(result)

        self.assertDictEqual(
            self.manager.status(name),
            {'paused': True, 'schedulable': False, 'locked': False}
        )

        self.manager.unpause(name)

    @my_vcr.use_cassette('pipeline/unpause_Consumer_Website')
    def test_unpause(self):
        name = "Consumer_Website"
        self.manager.pause(name, '')

        result = self.manager.unpause(name)
        self.assertIsNone(result)

        self.assertDictEqual(
            self.manager.status(name),
            {'paused': False, 'schedulable': True, 'locked': False}
        )

        # @my_vcr.use_cassette('pipeline/release_lock_Consumer_Website')
        # def test_release_lock(self):
        #     name = "Consumer_Website"
        #     self.manager.release_lock(name)
        #     # TODO: this fails, find a way to fix.

        # TODO: implement when schedule would be implemented
        # @my_vcr.use_cassette('pipeline/schedule_<name_of_pipeline>')
        # def test_schedule(self):
        #     self.fail()
