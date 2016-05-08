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

from six.moves.urllib.parse import urlencode

from yagocd.client import Yagocd
from yagocd.session import Session
from yagocd.resources import material

import pytest


class BaseTestConfigurationManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return material.MaterialManager(session=session)


class TestList(BaseTestConfigurationManager):
    def test_list_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("material/list") as cass:
            manager.list()
            assert cass.requests[0].path == '/go/api/config/materials'

    def test_list_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("material/list") as cass:
            manager.list()
            assert cass.requests[0].method == 'GET'

    def test_list_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("material/list") as cass:
            manager.list()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_list_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("material/list") as cass:
            manager.list()
            assert cass.responses[0]['status']['code'] == 200

    def test_list_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("material/list"):
            result = manager.list()
            assert all(isinstance(i, material.MaterialEntity) for i in result)


class TestModifications(BaseTestConfigurationManager):
    FINGERPRINT = 'e302ce7f43cd1a5009d218e7d6c1adf6a38fa9a33f6d0054d1607a00209fa810'

    def test_modifications_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("material/modifications") as cass:
            manager.modifications(self.FINGERPRINT)
            assert cass.requests[0].path == '/go/api/materials/{0}/modifications/{1}'.format(
                self.FINGERPRINT, 0
            )

    def test_modifications_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("material/modifications") as cass:
            manager.modifications(self.FINGERPRINT)
            assert cass.requests[0].method == 'GET'

    def test_modifications_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("material/modifications") as cass:
            manager.modifications(self.FINGERPRINT)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_modifications_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("material/modifications") as cass:
            manager.modifications(self.FINGERPRINT)
            assert cass.responses[0]['status']['code'] == 200

    def test_modifications_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("material/modifications"):
            result = manager.modifications(self.FINGERPRINT)
            assert all(isinstance(i, material.ModificationEntity) for i in result)


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


class TestNotifyGit(BaseTestConfigurationManager):
    URL = 'https://github.com/gocd-demo/services.git'

    def test_notify_git_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git") as cass:
            manager.notify_git(self.URL)
            assert cass.requests[0].path == '/go/api/material/notify/git'

    def test_notify_git_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git") as cass:
            manager.notify_git(self.URL)
            assert cass.requests[0].method == 'POST'

    def test_notify_git_request_data(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git") as cass:
            manager.notify_git(self.URL)
            assert cass.requests[0].body.decode('ascii') == urlencode({'repository_url': self.URL})

    def test_notify_git_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git") as cass:
            manager.notify_git(self.URL)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_notify_git_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git") as cass:
            manager.notify_git(self.URL)
            assert cass.responses[0]['status']['code'] == 202

    def test_notify_git_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("material/notify_git"):
            result = manager.notify_git(self.URL)
            assert result == ('The material is now scheduled for an update. '
                              'Please check relevant pipeline(s) for status.\n')
