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

import re
from distutils.version import LooseVersion

from easydict import EasyDict
# noinspection PyUnresolvedReferences
from six.moves import html_parser

from yagocd.resources import BaseManager
from yagocd.util import since


class AboutPageTableParser(html_parser.HTMLParser):
    def __init__(self):
        html_parser.HTMLParser.__init__(self)
        self._in_td = False
        self.data = list()

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self._in_td = True

    def handle_data(self, data):
        if self._in_td:
            self.data.append(data)

    def handle_endtag(self, tag):
        self._in_td = False


@since('14.3.0')
class InfoManager(BaseManager):
    """
    Class for getting general information about GoCD server.
    Mostly this class returns some system information about the
    server and not assumed to be used often.

    :versionadded: 14.3.0.

    Right now this class just parses /about page, for more robust approach
    you can use yagocd.resources.version.VersionManager class.
    """

    SERVER_VERSION_RE = re.compile(r'Server Version')
    VERSION_NUMBER_RE = re.compile(r'[\d.-]+')

    JVM_VERSION_RE = re.compile(r'JVM version')
    OS_INFO_RE = re.compile(r'OS Information')
    ARTIFACT_FREE_SPACE_RE = re.compile(r'Usable space in artifacts repository')
    DB_SCHEMA_VERSION_RE = re.compile(r'Database schema version')

    def __init__(self, session):
        super(InfoManager, self).__init__(session)
        self._parsed = None

    def _get_about_page(self):
        result = self._session.get(
            path='go/about',
            headers={'Accept': 'text/html'}
        )
        return result.text

    def _get_value(self, regex):
        if not self._parsed:
            content = self._get_about_page()

            parser = AboutPageTableParser()
            parser.feed(content)

            self._parsed = dict(zip(parser.data[0::2], parser.data[1::2]))

        for title, value in self._parsed.items():
            if regex.search(title):
                return value

    @property
    def version(self):
        value = self._get_value(self.SERVER_VERSION_RE)
        if value:
            match = self.VERSION_NUMBER_RE.match(value)
            if match:
                return match.group()

    @property
    def jvm_version(self):
        return self._get_value(self.JVM_VERSION_RE)

    @property
    def os_info(self):
        return self._get_value(self.OS_INFO_RE)

    @property
    def artifact_free_space(self):
        return self._get_value(self.ARTIFACT_FREE_SPACE_RE)

    @property
    def db_schema_version(self):
        return self._get_value(self.DB_SCHEMA_VERSION_RE)

    def support(self):
        """
        Method for getting different server support information.
        """
        response = self._session.get(
            path='{base_api}/support'.format(base_api=self.base_api),
            headers={
                'Accept': 'application/json',
            },
        )

        if LooseVersion(self._session.server_version) <= LooseVersion('16.3.0'):
            return response.text

        return EasyDict(response.json())

    def process_list(self):
        """
        Method for getting processes, executed by server.
        """
        response = self._session.get(
            path='{base_api}/process_list'.format(base_api=self.base_api),
            headers={
                'Accept': 'application/json',
            },
        )

        return EasyDict(response.json())
