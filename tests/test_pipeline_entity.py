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
    def test_has_all_managers_methods(self):
        excludes = ['tie_pipelines', 'list', 'find']

        def get_public_methods(klass):
            methods = set()
            for name in dir(klass):
                if name.startswith('_'):
                    continue

                candidate = getattr(klass, name)
                if hasattr(candidate, '__call__'):
                    methods.add(name)
            return methods

        managers_methods = get_public_methods(pipeline.PipelineManager)
        entity_methods = get_public_methods(pipeline.PipelineEntity)
        result = managers_methods - entity_methods - set(excludes)
        assert len(result) == 0, "Some methods are missing in pipeline entity: {}".format(result)

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

    def test_set_predecessors(self, pipeline_entity):
        value = [1, 3, 5]
        pipeline_entity.predecessors = value
        assert pipeline_entity.predecessors == value
        assert pipeline_entity.predecessors != pipeline_entity.descendants

    def test_get_predecessors(self, mock_session, pipeline_entity):
        child_1 = pipeline.PipelineEntity(mock_session, data=dict(name='child_1'))
        child_2 = pipeline.PipelineEntity(mock_session, data=dict(name='child_2'))
        child_3 = pipeline.PipelineEntity(mock_session, data=dict(name='child_3'))
        child_4 = pipeline.PipelineEntity(mock_session, data=dict(name='child_4'))

        child_2.predecessors = [child_1]
        child_3.predecessors = [child_1, child_2]
        child_4.predecessors = [child_3]
        pipeline_entity.predecessors = [child_4]

        assert pipeline_entity.get_predecessors() == [child_4]
        assert (sorted(pipeline_entity.get_predecessors(True), key=lambda x: x.data.name) ==
                [child_1, child_2, child_3, child_4])

        assert child_4.predecessors == [child_3]
        assert (sorted(child_4.get_predecessors(True), key=lambda x: x.data.name) ==
                [child_1, child_2, child_3])

        assert child_3.predecessors == [child_1, child_2]
        assert (sorted(child_3.get_predecessors(True), key=lambda x: x.data.name) ==
                [child_1, child_2])

        assert child_2.predecessors == [child_1]
        assert (sorted(child_2.get_predecessors(True), key=lambda x: x.data.name) == [child_1])

        assert child_1.predecessors == []
        assert (sorted(child_1.get_predecessors(True), key=lambda x: x.data.name) == [])

    def test_descendants_empty(self, pipeline_entity):
        assert pipeline_entity.descendants == list()

    def test_set_descendants(self, pipeline_entity):
        value = [2, 4, 8]
        pipeline_entity.descendants = value
        assert pipeline_entity.descendants == value
        assert pipeline_entity.predecessors != pipeline_entity.descendants

    def test_get_descendants(self, mock_session, pipeline_entity):
        parent_1 = pipeline.PipelineEntity(mock_session, data=dict(name='parent_1'))
        parent_2 = pipeline.PipelineEntity(mock_session, data=dict(name='parent_2'))
        parent_3 = pipeline.PipelineEntity(mock_session, data=dict(name='parent_3'))
        parent_4 = pipeline.PipelineEntity(mock_session, data=dict(name='parent_4'))

        parent_3.descendants = [parent_4]
        parent_2.descendants = [parent_4, parent_3]
        parent_1.descendants = [parent_2]
        pipeline_entity.descendants = [parent_1]

        assert pipeline_entity.get_descendants() == [parent_1]
        assert (sorted(pipeline_entity.get_descendants(True), key=lambda x: x.data.name) ==
                [parent_1, parent_2, parent_3, parent_4])

        assert parent_1.descendants == [parent_2]
        assert (sorted(parent_1.get_descendants(True), key=lambda x: x.data.name) ==
                [parent_2, parent_3, parent_4])

        assert parent_2.descendants == [parent_4, parent_3]
        assert (sorted(parent_2.get_descendants(True), key=lambda x: x.data.name) ==
                [parent_3, parent_4])

        assert parent_3.descendants == [parent_4]
        assert (sorted(parent_3.get_descendants(True), key=lambda x: x.data.name) == [parent_4])

        assert parent_4.descendants == []
        assert (sorted(parent_4.get_descendants(True), key=lambda x: x.data.name) == [])

    def test_get_url(self, pipeline_entity):
        assert (
            pipeline_entity.get_url('http://example.com', 'test_name') ==
            'http://example.com/go/tab/pipeline/history/test_name'
        )

    def test_url(self, pipeline_entity):
        assert pipeline_entity.url == 'http://example.com/go/tab/pipeline/history/pipeline_1'

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_call(self, history_mock, pipeline_entity):
        pipeline_entity.history()
        history_mock.assert_called_with(name=pipeline_entity.data.name, offset=0)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_full_history_call(self, history_mock, pipeline_entity):
        history_mock.side_effect = [['foo', 'bar', 'baz'], []]
        list(pipeline_entity.full_history())
        calls = [mock.call(pipeline_entity.data.name, 0), mock.call(pipeline_entity.data.name, 3)]
        history_mock.assert_has_calls(calls)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_last_call(self, history_mock, pipeline_entity):
        pipeline_entity.last()
        history_mock.assert_called_with(name=pipeline_entity.data.name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_last_returns_last(self, history_mock, pipeline_entity):
        history_mock.return_value = ['50', '30', '10']
        assert pipeline_entity.last() == '50'

    @mock.patch('yagocd.resources.pipeline.PipelineManager.get')
    def test_get_call(self, get_mock, pipeline_entity):
        pipeline_entity.get()
        get_mock.assert_called_with(name=pipeline_entity.data.name, counter=0)

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

    @mock.patch('yagocd.resources.pipeline.PipelineManager.schedule')
    def test_schedule_call(self, schedule_mock, pipeline_entity):
        pipeline_entity.schedule()
        schedule_mock.assert_called_with(name=pipeline_entity.data.name, materials=None, variables=None,
                                         secure_variables=None)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.schedule_with_instance')
    def test_schedule_with_instance_call(self, schedule_with_instance_mock, pipeline_entity):
        pipeline_entity.schedule_with_instance()
        schedule_with_instance_mock.assert_called_with(name=pipeline_entity.data.name, materials=None, variables=None,
                                                       secure_variables=None, backoff=0.5, max_tries=20)


class TestGraphDepthWalk(object):
    @pytest.mark.parametrize("root, expected", [
        ('a', ['a', 'c']),
        ('b', ['a', 'c', 'b']),
        ('c', ['c']),
        ('d', ['a', 'c', 'd']),
        ('e', ['a', 'c', 'b', 'e']),
    ])
    def test_graph(self, root, expected):
        graph = {'a': ['c'], 'b': ['a'], 'c': [], 'd': ['a'], 'e': ['b', 'a']}

        assert len(pipeline.PipelineEntity.graph_depth_walk(root, lambda x: graph.get(x))) == len(expected)
        assert sorted(pipeline.PipelineEntity.graph_depth_walk(root, lambda x: graph.get(x))) == sorted(expected)
