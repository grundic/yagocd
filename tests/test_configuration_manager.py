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
from six import string_types

from yagocd.client import Yagocd
from yagocd.session import Session
from yagocd.resources import configuration


class BaseTestConfigurationManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return configuration.ConfigurationManager(session=session)


class TestModifications(BaseTestConfigurationManager):
    def test_modifications_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.requests[0].path == '/go/api/config/revisions'

    def test_modifications_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.requests[0].method == 'GET'

    def test_modifications_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_modifications_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.responses[0]['status']['code'] == 200


class TestDiff(BaseTestConfigurationManager):
    start = '3336409d194252e8c82799472196e70cbe4c7916'
    end = '719be0bb99470b79fc48a949c24845f65a0fd8ef'

    def test_diff_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/diff") as cass:
            manager.diff(self.start, self.end)
            assert cass.requests[0].path == '/go/api/config/diff/{0}/{1}'.format(
                self.start, self.end
            )

    def test_diff_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/diff") as cass:
            manager.diff(self.start, self.end)
            assert cass.requests[0].method == 'GET'

    def test_diff_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/diff") as cass:
            manager.diff(self.start, self.end)
            assert cass.requests[0].headers['accept'] == 'text/plain'

    def test_diff_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/diff") as cass:
            manager.diff(self.start, self.end)
            assert cass.responses[0]['status']['code'] == 200

    def test_diff_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/diff"):
            result = manager.diff(self.start, self.end)
            assert isinstance(result, string_types)


class TestConfigCurrent(BaseTestConfigurationManager):
    def test_config_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_current") as cass:
            manager.config()
            assert cass.requests[0].path == '/go/api/admin/config/current.xml'

    def test_config_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_current") as cass:
            manager.config()
            assert cass.requests[0].method == 'GET'

    def test_config_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_current") as cass:
            manager.config()
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_config_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_current") as cass:
            manager.config()
            assert cass.responses[0]['status']['code'] == 200

    def test_config_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_current"):
            result = manager.config()
            assert isinstance(result, string_types)


class TestConfigMD5(BaseTestConfigurationManager):
    md5 = '412f48f7e2ff254e47564a6852ed7a2e'

    def test_config_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_md5") as cass:
            manager.config(self.md5)
            assert cass.requests[0].path == '/go/api/admin/config/{0}.xml'.format(self.md5)

    def test_config_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_md5") as cass:
            manager.config(self.md5)
            assert cass.requests[0].method == 'GET'

    def test_config_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_md5") as cass:
            manager.config(self.md5)
            assert cass.requests[0].headers['accept'] == 'application/xml'

    def test_config_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_md5") as cass:
            manager.config(self.md5)
            assert cass.responses[0]['status']['code'] == 200

    def test_config_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_md5"):
            result = manager.config(self.md5)
            assert isinstance(result, string_types)
