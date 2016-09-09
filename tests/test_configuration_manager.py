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

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import configuration


class BaseTestConfigurationManager(AbstractTestManager):
    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    def _execute_test_action(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def manager(self, session_fixture):
        return configuration.ConfigurationManager(session=session_fixture)


class TestModifications(BaseTestConfigurationManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            return cass, manager.modifications()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/config/revisions'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestDiff(BaseTestConfigurationManager, ReturnValueMixin):
    start = '3336409d194252e8c82799472196e70cbe4c7916'
    end = '719be0bb99470b79fc48a949c24845f65a0fd8ef'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/diff") as cass:
            return cass, manager.diff(self.start, self.end)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/config/diff/{0}/{1}'.format(self.start, self.end)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'text/plain'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestConfigCurrent(BaseTestConfigurationManager, ReturnValueMixin):
    TEST_METHOD_NAME = 'config'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_current") as cass:
            return cass, manager.config()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/config/current.xml'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/xml'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestConfigMD5(BaseTestConfigurationManager, ReturnValueMixin):
    TEST_METHOD_NAME = 'config'

    md5 = '412f48f7e2ff254e47564a6852ed7a2e'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/config_md5") as cass:
            return cass, manager.config(self.md5)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/config/{0}.xml'.format(self.md5)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/xml'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()
