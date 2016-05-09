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
import json

from yagocd.resources import pipeline
from yagocd.resources import stage
from yagocd.resources import Base
import pytest


class TestPipelineEntity(object):
    @pytest.fixture()
    def pipeline_instance(self, mock_session):
        data = json.load(open('tests/fixtures/resources/pipeline/pipeline_instance.json'))
        return pipeline.PipelineInstance(session=mock_session, data=data)

    def test_instance_is_not_none(self, pipeline_instance):
        assert pipeline_instance is not None

    def test_is_instance_of_base(self, pipeline_instance):
        assert isinstance(pipeline_instance, Base)

    def test_getting_name(self, pipeline_instance):
        assert pipeline_instance.data.name == 'Shared_Services'

    def test_getting_url(self, pipeline_instance):
        assert pipeline_instance.url == 'http://example.com/go/pipelines/value_stream_map/Shared_Services/2'

    def test_getting_pipeline_url(self, pipeline_instance):
        assert pipeline_instance.pipeline_url == 'http://example.com/go/tab/pipeline/history/Shared_Services'

    def test_stages_are_not_empty(self, pipeline_instance):
        assert len(pipeline_instance.stages()) > 0

    def test_stages_instances(self, pipeline_instance):
        assert all(isinstance(i, stage.StageInstance) for i in pipeline_instance.stages())
