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
import json

from yagocd.resources import pipeline
from yagocd.resources import stage
from yagocd.resources import Base
import mock


class TestPipelineEntity(TestCase):
    def setUp(self):
        self.patcher = mock.patch('yagocd.session.Session')
        self.mock_session = self.patcher.start()

        data = json.load(open('fixtures/resources/pipeline_instance.json'))

        self.instance = pipeline.PipelineInstance(session=self.mock_session, data=data)

    def test_is_instance_of_base(self):
        self.assertIsInstance(self.instance, Base)

    def test_construction(self):
        self.assertIsNotNone(self.instance)

    def test_getting_name(self):
        self.assertEqual(self.instance.data.name, 'Shared_Services')

    def test_stages_are_not_empty(self):
        self.assertGreater(len(self.instance.stages()), 0)

    def test_stages_instances(self):
        self.assertTrue(all(isinstance(i, stage.StageInstance) for i in self.instance.stages()))
