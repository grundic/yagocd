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
from yagocd.resources.pipeline import PipelineManager
from yagocd.session import Session


class Client(object):
    DEFAULT_OPTIONS = {
        'context_path': 'go/',
        'rest_base_path': 'api/',
        'verify': True,
        'headers': {
            'Accept': 'application/vnd.go.cd.v1+json',
        }
    }

    def __init__(self, server='http://localhost:8153', auth=None, options=None):
        options = {} if options is None else options

        options['server'] = server

        defaults = copy.deepcopy(self.DEFAULT_OPTIONS)
        options.update(defaults)

        self._session = Session(auth, options)

    @property
    def pipeline(self):
        return PipelineManager(session=self._session)


if __name__ == '__main__':
    pass
