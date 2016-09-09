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
from yagocd.resources import user


class BaseTestUserManager(AbstractTestManager):
    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    def _execute_test_action(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def manager(self, session_fixture):
        return user.UserManager(session=session_fixture)


class TestList(BaseTestUserManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/users'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(u, user.UserEntity) for u in result)

        return check_value


class TestGet(BaseTestUserManager, ReturnValueMixin):
    USERNAME = 'admin'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get") as cass:
            return cass, manager.get(self.USERNAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/users/{0}'.format(self.USERNAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return user.UserEntity

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


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


class TestUpdate(BaseTestUserManager, ReturnValueMixin):
    USERNAME = 'admin'
    OPTIONS = {
        'email': 'foo@bar.baz'
    }

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update") as cass:
            return cass, manager.update(self.USERNAME, self.OPTIONS)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/users/{0}'.format(self.USERNAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'PATCH'

    @pytest.fixture()
    def expected_return_type(self):
        return user.UserEntity

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.email == self.OPTIONS['email']

        return check_value


class TestDelete(BaseTestUserManager, ReturnValueMixin):
    USERNAME = 'user_02'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/delete") as cass:
            return cass, manager.delete(self.USERNAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/users/{0}'.format(self.USERNAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        return "User '{}' was deleted successfully.".format(self.USERNAME)
