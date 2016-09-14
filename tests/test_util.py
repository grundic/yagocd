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
from mock import mock

from yagocd.resources import pipeline
from yagocd.util import since, YagocdUtil


class TestBuildGraph(object):
    def test_tie_descendants(self, session_fixture):
        child_a = pipeline.PipelineEntity(
            session=session_fixture,
            data={'name': 'child1', 'materials': {}}
        )

        parent_a = pipeline.PipelineEntity(
            session=session_fixture,
            data={'name': 'parent1', 'materials': [{'description': 'child1', 'type': 'Pipeline'}]}
        )

        pipelines = [child_a, parent_a]

        YagocdUtil.build_graph(
            nodes=pipelines,
            dependencies=lambda parent: [material for material in parent.data.materials],
            compare=lambda candidate, child: candidate.description == child.data.name
        )
        assert child_a.descendants == [parent_a]


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

        assert len(YagocdUtil.graph_depth_walk(root, lambda x: graph.get(x))) == len(expected)
        assert sorted(YagocdUtil.graph_depth_walk(root, lambda x: graph.get(x))) == sorted(expected)


@pytest.mark.parametrize('since_version, expected_exc', [
    ('0.0.0', None),
    ('1.2.3.4', None),
    ('16.1.3', None),
    ('16.1.4', RuntimeError),
    ('17.1.3', RuntimeError),
])
class TestSinceDecorator(object):
    SERVER_VERSION = '16.1.3'

    @pytest.fixture()
    def dummy_cls(self):
        class Dummy(object):
            def __init__(self):
                self._session = mock.MagicMock()
                self._session.server_version = TestSinceDecorator.SERVER_VERSION

            def foo(self):
                pass

            def bar(self, baz):
                return baz * 10

        return Dummy

    def test_decorate_class(self, dummy_cls, since_version, expected_exc):
        decorated = since(since_version)(dummy_cls)
        assert callable(decorated.foo)
        assert callable(decorated.bar)
        assert decorated is dummy_cls

        assert decorated.foo.since_version == since_version
        assert decorated.bar.since_version == since_version

        if expected_exc:
            with pytest.raises(expected_exc):
                dummy_cls().foo()
            with pytest.raises(expected_exc):
                dummy_cls().bar(3)
        else:
            dummy_cls().foo()
            dummy_cls().bar(3)

    def test_decorate_method(self, dummy_cls, since_version, expected_exc):
        decorated_foo = since(since_version)(dummy_cls.foo)
        dummy_cls.foo = decorated_foo

        if expected_exc:
            with pytest.raises(expected_exc):
                dummy_cls().foo()
        else:
            dummy_cls().foo()
            dummy_cls().bar(3)

    def test_decorate_method_and_class(self, dummy_cls, since_version, expected_exc):
        decorated = since('1.1.1')(dummy_cls)

        decorated_foo = since(since_version)(dummy_cls.foo)
        dummy_cls.foo = decorated_foo

        assert decorated.foo.since_version == since_version
        assert decorated.bar.since_version == '1.1.1'
