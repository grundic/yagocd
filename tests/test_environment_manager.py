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

import pytest
from mock import mock
from six import string_types

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import environment


@pytest.fixture()
def manager(session_fixture):
    return environment.EnvironmentManager(session=session_fixture)


class BaseManager(AbstractTestManager):
    @pytest.fixture()
    def prepare_environment(self, manager, my_vcr):
        with my_vcr.use_cassette("environment/prepare"):
            manager.create(dict(name='foo'))
            manager.create(dict(name='bar', pipelines=[dict(name='Automated_Tests')]))


class TestList(BaseManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_environment):
        with my_vcr.use_cassette("environment/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/environments'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], list)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(i, environment.EnvironmentConfig) for i in result[0])

        return check_value


class TestGet(BaseManager, ReturnValueMixin):
    NAME = 'bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_environment):
        with my_vcr.use_cassette("environment/get_{}".format(self.NAME)) as cass:
            return cass, manager.get(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/environments/{}'.format(self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], environment.EnvironmentConfig)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.name == self.NAME

        return check_value


class TestCreate(BaseManager, ReturnValueMixin):
    NAME = 'baz'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("environment/create_{}".format(self.NAME)) as cass:
            return cass, manager.create(dict(name=self.NAME, pipelines=[dict(name='Shared_Services')]))

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/environments'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], environment.EnvironmentConfig)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.name == self.NAME
            assert result[0].data.pipelines[0].name == 'Shared_Services'

        return check_value


class TestUpdate(BaseManager, ReturnValueMixin):
    NAME = 'bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_environment):
        with my_vcr.use_cassette("environment/prepare_update_{}".format(self.NAME)):
            env, etag = manager.get(self.NAME)
        with my_vcr.use_cassette("environment/update_{}".format(self.NAME)) as cass:
            env.data.pipelines.append(dict(name='Deploy_UAT'))
            return cass, manager.update(name=self.NAME, config=dict(name='new_name'), etag=etag)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/environments/{}'.format(self.NAME)

    @pytest.fixture()
    def expected_request_method(self, manager):
        if LooseVersion(manager._session.server_version) <= LooseVersion('16.9.0'):
            return 'PATCH'
        return 'PUT'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], environment.EnvironmentConfig)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.name == 'new_name'

        return check_value


class TestDelete(BaseManager, ReturnValueMixin):
    NAME = 'foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_environment):
        with my_vcr.use_cassette("environment/delete_{}".format(self.NAME)) as cass:
            return cass, manager.delete(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/environments/{}'.format(self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result == "Environment '{}' was deleted successfully.".format(self.NAME)

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.environment.EnvironmentManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        name = mock.MagicMock()
        _ = manager[name]  # noqa
        get_mock.assert_called_once_with(name=name)

    @mock.patch('yagocd.resources.environment.EnvironmentManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
