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

import copy
from yagocd.session import Session
from yagocd.resources.agent import AgentManager
from yagocd.resources.user import UserManager
from yagocd.resources.material import MaterialManager
from yagocd.resources.stage import StageManager
from yagocd.resources.pipeline import PipelineManager
from yagocd.resources.property import PropertyManager
from yagocd.resources.configuration import ConfigurationManager
from yagocd.resources.feed import FeedManager


class Client(object):
    DEFAULT_OPTIONS = {
        'context_path': 'go/',
        'api_path': 'api/',
        'verify': True,
        'headers': {
            'Accept': 'application/vnd.go.cd.v1+json',
        }
    }

    def __init__(self, server='http://localhost:8153', auth=None, options=None):
        options = {} if options is None else options

        options['server'] = server

        merged = copy.deepcopy(self.DEFAULT_OPTIONS)
        merged.update(options)

        self._session = Session(auth, merged)

    @property
    def agent(self):
        return AgentManager(session=self._session)

    @property
    def user(self):
        return UserManager(session=self._session)

    @property
    def material(self):
        return MaterialManager(session=self._session)

    @property
    def pipeline(self):
        return PipelineManager(session=self._session)

    @property
    def stage(self):
        return StageManager(session=self._session)

    @property
    def properties(self):
        return PropertyManager(session=self._session)

    @property
    def configuration(self):
        return ConfigurationManager(session=self._session)

    @property
    def feed(self):
        return FeedManager(session=self._session)


if __name__ == '__main__':
    pass
