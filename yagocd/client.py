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
from urlparse import urljoin

from yagocd.resources.pipeline import PipelineManager
import requests


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

        self._options = copy.deepcopy(self.DEFAULT_OPTIONS)
        self._options.update(options)
        self._auth = auth

        self._pipeline = PipelineManager(self)

    @staticmethod
    def urljoin(*args):
        """
        Joins given arguments into a url. Trailing but not leading slashes are
        stripped for each argument.
        """
        return "/".join(map(lambda x: str(x).rstrip('/'), args))

    def request(self, method, path, data=None, headers=None):
        # TODO: think how to make this method private.
        # One possibility is to create internal variable with baseurl for making all requests.

        # this should work even if path is absolute (e.g. for files)
        url = urljoin(self._options['server'], path)

        if headers is None:
            headers = self._options['headers']
        response = requests.request(
            method=method,
            url=url,
            auth=self._auth,
            data=data,
            verify=self._options['verify'],
            headers=headers
        )
        # raise exception if we got 4xx/5xx response
        response.raise_for_status()

        return response

    def get(self, path, headers=None):
        return self.request(method='get', path=path, headers=headers)

    def post(self, path, data=None, headers=None):
        return self.request(method='post', path=path, data=data, headers=headers)

    def base_api(self, context_path=None, rest_base_path=None):
        # TODO: think how to make this method private.
        # One possibility is to create internal variable with baseurl for making all requests.
        return self.urljoin(
            context_path or self._options['context_path'],
            rest_base_path or self._options['rest_base_path']
        )

    @property
    def pipeline(self):
        return self._pipeline


if __name__ == '__main__':
    pass

