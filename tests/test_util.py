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
from yagocd.util import YagocdUtil
import pytest


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
