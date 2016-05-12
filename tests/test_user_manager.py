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
from yagocd.resources import user


class BaseTestUserManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=('admin', '12345'), options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return user.UserManager(session=session)


class TestList(BaseTestUserManager):
    def test_list_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("user/list") as cass:
            manager.list()
            assert cass.requests[0].path == '/go/api/users'

    def test_list_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("user/list") as cass:
            manager.list()
            assert cass.requests[0].method == 'GET'

    def test_list_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("user/list") as cass:
            manager.list()
            assert cass.requests[0].headers['accept'] == 'application/vnd.go.cd.v1+json'

    def test_list_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("user/list") as cass:
            manager.list()
            assert cass.responses[0]['status']['code'] == 200

    def test_list_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("user/list"):
            result = manager.list()
            assert all(isinstance(u, user.UserEntity) for u in result)


class TestGet(BaseTestUserManager):
    USERNAME = 'admin'

    def test_get_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get") as cass:
            manager.get(self.USERNAME)
            assert cass.requests[0].path == '/go/api/users/{0}'.format(self.USERNAME)

    def test_get_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get") as cass:
            manager.get(self.USERNAME)
            assert cass.requests[0].method == 'GET'

    def test_get_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get") as cass:
            manager.get(self.USERNAME)
            assert cass.requests[0].headers['accept'] == 'application/vnd.go.cd.v1+json'

    def test_get_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get") as cass:
            manager.get(self.USERNAME)
            assert cass.responses[0]['status']['code'] == 200

    def test_get_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get"):
            result = manager.get(self.USERNAME)
            assert isinstance(result, user.UserEntity)
#
#
# class TestCreate(BaseTestUserManager):
#     OPTIONS = {
#         'login_name': 'foobar',
#         'enabled': True,
#         'email': 'foo@bar.baz',
#         'email_me': False,
#         'checkin_aliases': ['foo', 'bar', 'baz']
#     }
#
#     def test_create_request_url(self, manager, my_vcr):
#         with my_vcr.use_cassette("user/create") as cass:
#             manager.create(self.OPTIONS)
#             assert cass.requests[0].path == '/go/api/users'
#
#     def test_create_request_method(self, manager, my_vcr):
#         with my_vcr.use_cassette("user/create") as cass:
#             manager.create(self.OPTIONS)
#             assert cass.requests[0].method == 'POST'
#
#     def test_create_request_accept_headers(self, manager, my_vcr):
#         with my_vcr.use_cassette("user/create") as cass:
#             manager.create(self.OPTIONS)
#             assert cass.requests[0].headers['accept'] == 'application/json'
#
#     def test_create_response_code(self, manager, my_vcr):
#         with my_vcr.use_cassette("user/create") as cass:
#             manager.create(self.OPTIONS)
#             assert cass.responses[0]['status']['code'] == 200
#
#     def test_create_return_type(self, manager, my_vcr):
#         with my_vcr.use_cassette("user/create"):
#             result = manager.create(self.OPTIONS)
#             assert isinstance(result, user.UserEntity)


class TestUpdate(BaseTestUserManager):
    USERNAME = 'admin'
    OPTIONS = {
        'email': 'foo@bar.baz'
    }

    def test_update_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update") as cass:
            manager.update(self.USERNAME, self.OPTIONS)
            assert cass.requests[0].path == '/go/api/users/{0}'.format(self.USERNAME)

    def test_update_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update") as cass:
            manager.update(self.USERNAME, self.OPTIONS)
            assert cass.requests[0].method == 'PATCH'

    def test_update_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update") as cass:
            manager.update(self.USERNAME, self.OPTIONS)
            assert cass.requests[0].headers['accept'] == 'application/vnd.go.cd.v1+json'

    def test_update_request_content_type_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update") as cass:
            manager.update(self.USERNAME, self.OPTIONS)
            assert cass.requests[0].headers['Content-Type'] == 'application/json'

    def test_update_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update") as cass:
            manager.update(self.USERNAME, self.OPTIONS)
            assert cass.responses[0]['status']['code'] == 200

    def test_update_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update"):
            result = manager.update(self.USERNAME, self.OPTIONS)
            assert isinstance(result, user.UserEntity)

    def test_update_return_value(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update"):
            result = manager.update(self.USERNAME, self.OPTIONS)
            assert result.data.email == self.OPTIONS['email']


class TestDelete(BaseTestUserManager):
    USERNAME = 'user_02'

    def test_delete_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("user/delete") as cass:
            manager.delete(self.USERNAME)
            assert cass.requests[0].path == '/go/api/users/{0}'.format(self.USERNAME)

    def test_delete_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("user/delete") as cass:
            manager.delete(self.USERNAME)
            assert cass.requests[0].method == 'DELETE'

    def test_delete_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("user/delete") as cass:
            manager.delete(self.USERNAME)
            assert cass.requests[0].headers['accept'] == 'application/vnd.go.cd.v1+json'

    def test_delete_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("user/delete") as cass:
            manager.delete(self.USERNAME)
            assert cass.responses[0]['status']['code'] == 200

    def test_delete_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("user/delete"):
            result = manager.delete(self.USERNAME)
            assert isinstance(result, string_types)
