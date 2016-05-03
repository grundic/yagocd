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

from yagocd.resources import BaseManager


class ConfigurationManager(BaseManager):
    """
    The configuration API allows users with administration role
    to view and manage configuration.
    """

    def modifications(self):
        """
        Lists the config repository modifications.

        :return: An array of repository modifications.
        """
        response = self._session.get(
            path='{base_api}/config/revisions'.format(base_api=self.base_api),
            headers={'Accept': 'application/json'},
        )

        return response.json()

    def diff(self, start, end):
        """
        Gets the diff between two config repository modifications.

        :param start: starting SHA commit.
        :param end: ending SHA commit.
        :return: the diff between two config repo modifications.
        """
        response = self._session.get(
            path='{base_api}/config/diff/{start}/{end}'.format(
                base_api=self.base_api,
                start=start,
                end=end
            ),
            headers={'Accept': 'text/plain'},
        )

        return response.text

    def config(self, md5=None):
        """
        Gets the current configuration file.

        :param md5: md5 sum of config to get. If not given, current will be returned.
        :return: the contents of the configuration file.
        """
        response = self._session.get(
            path='{base_api}/admin/config/{version}'.format(
                base_api=self.base_api,
                version='current.xml' if md5 is None else (md5 + '.xml'),
            ),
            headers={'Accept': 'application/xml'},
        )

        return response.text
