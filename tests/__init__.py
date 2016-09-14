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
import inspect
import re
from distutils.version import LooseVersion

import pytest


class AbstractTestManager(object):
    TEST_METHOD_NAME = None
    EXPECTED_CASSETTE_COUNT = 1

    @staticmethod
    def _camel_to_underscore(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _test_method_name(self):
        name_from_class = self._camel_to_underscore(self.__class__.__name__.replace('Test', ''))
        return self.TEST_METHOD_NAME or name_from_class

    @pytest.fixture(autouse=True)
    def _is_method_supported(self, manager, server_version):
        method = getattr(manager, self._test_method_name())

        since_version = method.since_version
        if LooseVersion(server_version) < since_version:
            pytest.skip("Method `{name}` is not supported on '{server_version}'".format(
                name=method.__name__, server_version=server_version
            ))

    @pytest.fixture(autouse=True)
    def check_cassette_len(self, _execute_test_action):
        cass, result = _execute_test_action
        if self.EXPECTED_CASSETTE_COUNT is None:
            pytest.skip("Unpredictable request count.")
            return
        assert len(cass) == self.EXPECTED_CASSETTE_COUNT

    @pytest.fixture()
    def _execute_test_action(self, *args, **kwargs):
        """
        Method that should execute tested function with help of vcr.
        Expected to return two parameters: cassette and execution result.
        """
        raise NotImplementedError()

    @pytest.fixture()
    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def expected_accept_headers(self, *args, **kwargs):
        return 'application/vnd.go.cd.v1+json'

    @pytest.fixture()
    def expected_response_code(self, *args, **kwargs):
        return 200

    @pytest.fixture()
    def server_version(self, manager, my_vcr):
        """
        Special fixture to get server version from recorded cassette.
        """
        with my_vcr.use_cassette("server_version_cache/server_version_cache"):
            return manager._session.server_version

    def test_request_url(self, _execute_test_action, expected_request_url):
        cass, result = _execute_test_action
        assert cass.requests[0].path == expected_request_url

    def test_request_method(self, _execute_test_action, expected_request_method):
        cass, result = _execute_test_action
        assert cass.requests[0].method == expected_request_method

    def test_request_accept_headers(self, _execute_test_action, expected_accept_headers):
        cass, result = _execute_test_action
        actual = cass.requests[0].headers['accept']
        assert actual == expected_accept_headers

    def test_response_code(self, _execute_test_action, expected_response_code):
        cass, result = _execute_test_action
        assert cass.responses[0]['status']['code'] == expected_response_code


class RequestContentTypeHeadersMixin(object):
    @pytest.fixture()
    def expected_content_type_headers(self, *args, **kwargs):
        raise NotImplementedError()

    def test_update_request_content_type_headers(self, _execute_test_action, expected_content_type_headers):
        cass, result = _execute_test_action
        assert cass.requests[0].headers['content-type'] == expected_content_type_headers


class ReturnValueMixin(object):
    @pytest.fixture()
    def expected_return_type(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def expected_return_value(self, *args, **kwargs):
        raise NotImplementedError()

    def test_return_type(self, _execute_test_action, expected_return_type):
        cass, result = _execute_test_action

        if callable(expected_return_type) and not inspect.isclass(expected_return_type):
            expected_return_type(result)
        elif result is None:
            assert expected_return_type is None
            pytest.skip("Skipping checking return type as method is not returning anything")
            return
        else:
            assert isinstance(result, expected_return_type)

    def test_return_value(self, _execute_test_action, expected_return_value):
        cass, result = _execute_test_action

        if callable(expected_return_value):
            expected_return_value(result)
        elif result is None:
            assert expected_return_value is None
            pytest.skip("Skipping checking return value as method is not returning anything")
            return
        else:
            assert result == expected_return_value


class ConfirmHeaderMixin(object):
    def test_confirm_header(self, _execute_test_action):
        cass, result = _execute_test_action
        assert cass.requests[0].headers['Confirm'] == 'true'
