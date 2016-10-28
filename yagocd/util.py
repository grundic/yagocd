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
import functools
import inspect
from collections import deque
from distutils.version import LooseVersion


class YagocdUtil(object):
    @staticmethod
    def build_graph(nodes, dependencies, compare):
        for child in nodes:
            parents = list()

            for parent in nodes:
                children = list()

                for child_candidate in dependencies(parent):
                    if compare(child_candidate, child):
                        parents.append(parent)
                        children.append(child)
                parent.predecessors.extend(children)
            child.descendants = parents
        return nodes

    @staticmethod
    def graph_depth_walk(root_nodes, near_nodes):

        visited = set()
        to_crawl = deque(root_nodes)
        while to_crawl:
            current = to_crawl.popleft()
            if current in visited:
                continue
            visited.add(current)
            node_children = set(near_nodes(current))
            to_crawl.extend(node_children - visited)
        return list(visited)

    @classmethod
    def choose_option(cls, version_to_options, default, server_version):
        for version in sorted([LooseVersion(v) for v in version_to_options.keys()]):
            if LooseVersion(server_version) <= version:
                return version_to_options[version.vstring]

        return default


class Since(object):
    # Parameter for controlling version compatibility checks.
    # Setting this to `False` will skip checking the server
    # version on each function call.
    ENABLED = True

    def __init__(self, since_version):
        self._since_version = LooseVersion(since_version)

    def __call__(self, entity):
        @functools.wraps(entity)
        def decorated(*args, **kwargs):
            if self.ENABLED:
                this = args[0]
                server_version = this._session.server_version
                if LooseVersion(server_version) < self._since_version:
                    name = "{}.{}".format(this.__class__.__name__, entity.__name__)
                    raise RuntimeError(
                        "Method `{name}` is not supported on '{server_version}' "
                        "version of GoCD, it has been added only in '{since_version}' version!".format(
                            name=name,
                            server_version=server_version,
                            since_version=self._since_version
                        )
                    )

            return entity(*args, **kwargs)

        if inspect.isclass(entity):
            for item in vars(entity):
                if item.startswith('_'):
                    continue
                candidate = getattr(entity, item)
                if callable(candidate) and not hasattr(candidate, 'since_version'):
                    decorated_candidate = self.__class__(self._since_version.vstring)(candidate)
                    setattr(entity, item, decorated_candidate)

            return entity
        else:
            decorated.since_version = self._since_version  # used to skip tests on unsupported versions
            return decorated


since = Since
