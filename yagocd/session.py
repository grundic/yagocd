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

import copy

import requests
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urljoin

from yagocd.exception import RequestError


class Session(object):
    """
    Class for working with sessions.
    Instance of this class is created only once in the initialization of ``yagocd.client.Client`` and then passed
    as a parameter for all managers.
    """

    def __init__(self, auth, options):
        self._auth = auth
        self._options = options
        self._session = requests.Session()
        self.__server_version = None

    @staticmethod
    def urljoin(*args):
        """
        Joins given arguments into a url. Trailing but not leading slashes are
        stripped for each argument.
        """
        return "/".join(map(lambda x: str(x).rstrip('/'), args)).rstrip('/')

    @property
    def server_url(self):
        """
        Property for getting server url.

        :return: server url for this instance.
        """
        return self._options['server'].rstrip('/')

    @property
    def server_version(self):
        """
        Special method for getting server version.

        Because of different behaviour on different versions of
        server, we have to pass different headers to the endpoints.
        This method requests the version from server and caches it
        in internal variable, so other resources could use it.

        :return: server version parsed from `about` page.
        """
        if self.__server_version is None:
            from yagocd.resources.info import InfoManager
            self.__server_version = InfoManager(self).version

        return self.__server_version

    def request(self, method, path, params=None, data=None, headers=None, files=None):
        # this should work even if path is absolute (e.g. for files)
        url = urljoin(self._options['server'], path)

        merged_headers = copy.deepcopy(self._options['headers'])
        merged_headers.update(headers or {})

        response = self._session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=merged_headers,
            files=files,
            auth=self._auth,
            verify=self._options['verify']
        )
        # raise exception if we got 4xx/5xx response
        self._raise_for_status(response)

        return response

    @staticmethod
    def _raise_for_status(response):
        summary = ''

        if 400 <= response.status_code < 500:
            summary = '[%s] Client Error: %s for url: %s' % (response.status_code, response.reason, response.url)

        elif 500 <= response.status_code < 600:
            summary = '[%s] Server Error: %s for url: %s' % (response.status_code, response.reason, response.url)

        if summary:
            raise RequestError(summary=summary, response=response)

    def get(self, path, params=None, headers=None):
        return self.request(method='get', path=path, params=params, headers=headers)

    def post(self, path, params=None, data=None, headers=None, files=None):
        return self.request(method='post', path=path, params=params, data=data, headers=headers, files=files)

    def put(self, path, data=None, headers=None, files=None):
        return self.request(method='put', path=path, data=data, headers=headers, files=files)

    def patch(self, path, data=None, headers=None):
        return self.request(method='patch', path=path, data=data, headers=headers)

    def delete(self, path, data=None, headers=None):
        return self.request(method='delete', path=path, data=data, headers=headers)

    def base_api(self, context_path=None, api_path=None):
        return self.urljoin(
            context_path if context_path is not None else self._options['context_path'],
            api_path if api_path is not None else self._options['api_path']
        )


if __name__ == '__main__':
    pass
