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
from distutils.version import LooseVersion

import mock
import pytest
from six import string_types

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import info


class BaseTestInfoManager(object):
    @pytest.fixture()
    def manager(self, session_fixture):
        return info.InfoManager(session=session_fixture)


class TestVersion(BaseTestInfoManager):
    def test_result_is_not_none(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page"):
            result = manager.version
            assert result is not None

    def test_multiple_call(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page") as cass:
            for x in range(10):
                result = manager.version
                assert result is not None

            assert len(cass.requests) == 1

    @mock.patch('yagocd.resources.info.InfoManager._get_value')
    def test_unmatched_version(self, get_value_mock, manager, my_vcr):
        get_value_mock.return_value = 'unsupported-version-number'

        with my_vcr.use_cassette("info/about_page"):
            result = manager.version
            assert result is None


class TestJvmVersion(BaseTestInfoManager):
    def test_result_is_not_none(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page"):
            result = manager.jvm_version
            assert result is not None

    def test_multiple_call(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page") as cass:
            for x in range(10):
                result = manager.jvm_version
                assert result is not None

            assert len(cass.requests) == 1


class TestOsInfo(BaseTestInfoManager):
    def test_result_is_not_none(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page"):
            result = manager.os_info
            assert result is not None

    def test_multiple_call(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page") as cass:
            for x in range(10):
                result = manager.os_info
                assert result is not None

            assert len(cass.requests) == 1


class TestArtifactFreeSpace(BaseTestInfoManager):
    def test_result_is_not_none(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page"):
            result = manager.artifact_free_space
            assert result is not None

    def test_multiple_call(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page") as cass:
            for x in range(10):
                result = manager.artifact_free_space
                assert result is not None

            assert len(cass.requests) == 1


class TestDbSchemaVersion(BaseTestInfoManager):
    def test_result_is_not_none(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page"):
            result = manager.db_schema_version
            assert result is not None

    def test_multiple_call(self, manager, my_vcr):
        with my_vcr.use_cassette("info/about_page") as cass:
            for x in range(10):
                result = manager.db_schema_version
                assert result is not None

            assert len(cass.requests) == 1


class TestSupport(BaseTestInfoManager, AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("info/support") as cass:
            return cass, manager.support()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/support'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, *args, **kwargs):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self, manager):
        if LooseVersion(manager._session.server_version) <= LooseVersion('16.3.0'):
            return string_types
        return dict

    @pytest.fixture()
    def expected_return_value(self, manager, gocd_docker):
        def check_value(result):
            if LooseVersion(manager._session.server_version) <= LooseVersion('16.3.0'):
                assert gocd_docker in result
            else:
                assert result["Go Server Information"]["Version"].startswith(gocd_docker)

        return check_value


class TestProcessList(BaseTestInfoManager, AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("info/process_list") as cass:
            return cass, manager.process_list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/process_list'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, *args, **kwargs):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return dict

    @pytest.fixture()
    def expected_return_value(self, gocd_docker):
        pytest.skip()
