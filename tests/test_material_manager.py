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

from tests import AbstractTestManager, ConfirmHeaderMixin, ReturnValueMixin
from yagocd.resources import material


class BaseTestConfigurationManager(AbstractTestManager):
    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    def _execute_test_action(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def manager(self, session_fixture):
        return material.MaterialManager(session=session_fixture)


class TestList(BaseTestConfigurationManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("material/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/config/materials'

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
        def check_value(result):
            assert all(isinstance(i, material.MaterialEntity) for i in result)

        return check_value


class TestModifications(BaseTestConfigurationManager, ReturnValueMixin):
    FINGERPRINT = 'e302ce7f43cd1a5009d218e7d6c1adf6a38fa9a33f6d0054d1607a00209fa810'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("material/modifications") as cass:
            return cass, manager.modifications(self.FINGERPRINT)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/materials/{0}/modifications/{1}'.format(
            self.FINGERPRINT, 0
        )

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
        def check_value(result):
            assert all(isinstance(i, material.ModificationEntity) for i in result)

        return check_value


#
# class TestNotifySvn(BaseTestConfigurationManager):
#     UUID = ''
#
#     def test_notify_svn_request_url(self, manager, my_vcr):
#         with my_vcr.use_cassette("material/notify_svn") as cass:
#             manager.notify_svn(self.UUID)
#             assert cass.requests[0].path == '/material/notify/svn'
#
#     def test_notify_svn_request_method(self, manager, my_vcr):
#         with my_vcr.use_cassette("material/notify_svn") as cass:
#             manager.notify_svn(self.UUID)
#             assert cass.requests[0].method == 'POST'
#
#     def test_notify_svn_request_data(self, manager, my_vcr):
#         with my_vcr.use_cassette("material/notify_svn") as cass:
#             manager.notify_svn(self.UUID)
#             assert False  # add check for uuid in data
#
#     def test_notify_svn_request_accept_headers(self, manager, my_vcr):
#         with my_vcr.use_cassette("material/notify_svn") as cass:
#             manager.notify_svn(self.UUID)
#             assert cass.requests[0].headers['accept'] == 'application/json'
#
#     def test_notify_svn_response_code(self, manager, my_vcr):
#         with my_vcr.use_cassette("material/notify_svn") as cass:
#             manager.notify_svn(self.UUID)
#             assert cass.responses[0]['status']['code'] == 200
#
#     def test_notify_svn_return_type(self, manager, my_vcr):
#         with my_vcr.use_cassette("material/notify_svn"):
#             result = manager.notify_svn(self.UUID)
#             assert all(isinstance(i, material.ModificationEntity) for i in result)


class TestNotifyGit(BaseTestConfigurationManager, ReturnValueMixin, ConfirmHeaderMixin):
    URL = 'https://github.com/grundic/yagocd.git'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git") as cass:
            return cass, manager.notify_git(self.URL)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/material/notify/git'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_response_code(self, *args, **kwargs):
        return 202

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        return 'The material is now scheduled for an update. Please check relevant pipeline(s) for status.\n'
