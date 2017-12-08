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
from mock import mock
from six import string_types

from tests import AbstractTestManager, ReturnValueMixin
from distutils.version import LooseVersion
from yagocd.resources import user


@pytest.fixture()
def manager(session_fixture):
    return user.UserManager(session=session_fixture)


@pytest.fixture(autouse=True)
def skip_by_gocd_version(request, gocd_docker):
    if gocd_docker.startswith('v'):
        gocd_docker = gocd_docker[1:]

    if request.node.get_marker('works_after'):
        works_after_version = request.node.get_marker('works_after').args[0]
        if LooseVersion(gocd_docker) < LooseVersion(works_after_version):
            pytest.skip('This test works only after {}'.format(works_after_version))


class TestList(AbstractTestManager, ReturnValueMixin):
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


class TestGet(AbstractTestManager, ReturnValueMixin):
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
        def check_value(result):
            assert result.data.login_name == 'admin'

        return check_value


class TestCurrent(AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/get_current") as cass:
            return cass, manager.current()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/current_user'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return user.UserEntity

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.login_name == 'admin'

        return check_value


@pytest.mark.works_after('17.1.0')
class TestCreate(AbstractTestManager, ReturnValueMixin):
    OPTIONS = {
        'login_name': 'foobar',
        'enabled': True,
        'email': 'foo@bar.baz',
        'email_me': False,
        'checkin_aliases': ['foo', 'bar', 'baz']
    }

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/create") as cass:
            return cass, manager.create(self.OPTIONS)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/users'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_response_code(self, *args, **kwargs):
        return 201

    @pytest.fixture()
    def expected_return_type(self):
        return user.UserEntity

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.login_name == 'foobar'

        return check_value


class TestUpdate(AbstractTestManager, ReturnValueMixin):
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


class TestUpdateCurrent(AbstractTestManager, ReturnValueMixin):
    OPTIONS = {
        'email': 'admin@gocd.com'
    }

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("user/update_current") as cass:
            return cass, manager.update_current(self.OPTIONS)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/current_user'

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


class TestDelete(AbstractTestManager, ReturnValueMixin):
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
        def check_value(result):
            assert result in [
                "User '{}' was deleted successfully.".format(self.USERNAME),
                "The user '{}' was deleted successfully.".format(self.USERNAME),
            ]

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.user.UserManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        login = mock.MagicMock()
        _ = manager[login]  # noqa
        get_mock.assert_called_once_with(login=login)

    @mock.patch('yagocd.resources.user.UserManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
