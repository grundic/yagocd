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

from easydict import EasyDict

from yagocd.util import YagocdUtil


class BaseManager(object):
    # Default accept header to be used in client.
    # This variable is used a default for all requests, but
    # at the same time individual managers could overwrite it.
    ACCEPT_HEADER = 'application/vnd.go.cd.v1+json'

    # This map configures pessimistic acceptance header resolve:
    # by default the `ACCEPT_HEADER` would be used, but in case
    # server version is less or equal one of these, then it would
    # be overwritten from mapping.
    # It can be read as `up to given version use next header`.
    # This variable should be ordered, so please use `OrderedDict`
    # to define it.
    VERSION_TO_ACCEPT_HEADER = None

    def __init__(self, session):
        """
        :type session: yagocd.session.Session
        """
        self._session = session
        self.base_api = self._session.base_api()

    def _accept_header(self):
        """
        Method for determining correct `Accept` header.

        Different resources and different GoCD version servers prefer
        a diverse headers. In order to manage all of them, this method
        tries to help: if `VERSION_TO_ACCEPT_HEADER` is not provided,
        if would simply return default `ACCEPT_HEADER`.
        Though if some manager specifies `VERSION_TO_ACCEPT_HEADER`
        class variable, then it should be a dictionary: keys should be
        a versions and values should be desired accept headers.
        Choosing is pessimistic: if version of a server is less or
        equal to one of the dictionary, the value of that key would be
        used.

        :return: accept header to use in request.
        """
        if not self.VERSION_TO_ACCEPT_HEADER:
            return self.ACCEPT_HEADER

        return YagocdUtil.choose_option(
            version_to_options=self.VERSION_TO_ACCEPT_HEADER,
            default=self.ACCEPT_HEADER,
            server_version=self._session.server_version
        )


class Base(object):
    def __init__(self, session, data):
        self._session = session
        self._data = EasyDict(data)

        self.base_api = self._session.base_api()

    @property
    def data(self):
        return self._data

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()


class BaseNode(Base):
    def __init__(self, session, data):
        super(BaseNode, self).__init__(session, data)

        self._predecessors = list()
        self._descendants = list()

    def get_predecessors(self, transitive=False):
        """
        Property for getting predecessors (parents) of current pipeline.
        This property automatically populates from API call

        :return: list of :class:`yagocd.resources.pipeline.PipelineEntity`.
        :rtype: list of yagocd.resources.pipeline.PipelineEntity
        """
        result = self._predecessors
        if transitive:
            return YagocdUtil.graph_depth_walk(result, lambda v: v.predecessors)
        return result

    def set_predecessors(self, value):
        self._predecessors = value

    predecessors = property(get_predecessors, set_predecessors)

    def get_descendants(self, transitive=False):
        """
        Property for getting descendants (children) of current pipeline.
        It's calculated by :meth:`yagocd.resources.pipeline.PipelineManager#tie_descendants` method during listing of
        all pipelines.

        :return: list of :class:`yagocd.resources.pipeline.PipelineEntity`.
        :rtype: list of yagocd.resources.pipeline.PipelineEntity
        """
        result = self._descendants
        if transitive:
            return YagocdUtil.graph_depth_walk(result, lambda v: v.descendants)
        return result

    def set_descendants(self, value):
        self._descendants = value

    descendants = property(get_descendants, set_descendants)
