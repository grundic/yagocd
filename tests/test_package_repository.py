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
from yagocd.resources import package_repository


@pytest.fixture()
def manager(session_fixture):
    return package_repository.PackageRepositoryManager(session=session_fixture)


class BaseManager(AbstractTestManager):
    @pytest.fixture()
    def prepare_package_repositories(self, manager, my_vcr):
        with my_vcr.use_cassette("package_repositories/prepare"):
            manager.create(dict(
                repo_id='repository-foo',
                name='repo.foo',
                plugin_metadata=dict(id="yum", version="1"),
                configuration=[
                    dict(key="REPO_URL", value="http://foo.example.com")
                ]
            ))

            manager.create(dict(
                repo_id='repository-bar',
                name='repo.bar',
                plugin_metadata=dict(id="yum", version="1"),
                configuration=[
                    dict(key="REPO_URL", value="http://bar.example.com")
                ]
            ))


class TestList(BaseManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_package_repositories):
        with my_vcr.use_cassette("package_repositories/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/repositories'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(i, package_repository.PackageRepository) for i in result)

        return check_value


class TestGet(BaseManager, ReturnValueMixin):
    ID = 'repository-foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_package_repositories):
        with my_vcr.use_cassette("package_repositories/get_{}".format(self.ID)) as cass:
            return cass, manager.get(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/repositories/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return package_repository.PackageRepository

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.repo_id == self.ID

        return check_value


class TestCreate(BaseManager, ReturnValueMixin):
    ID = 'repository-baz'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("package_repositories/create_{}".format(self.ID)) as cass:
            return cass, manager.create(dict(
                repo_id=self.ID,
                name='repo.baz',
                plugin_metadata=dict(id="yum", version="1"),
                configuration=[
                    dict(key="REPO_URL", value="http://baz.example.com")
                ]
            ))

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/repositories'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        return package_repository.PackageRepository

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.repo_id == self.ID
            assert result.data.name == 'repo.baz'

        return check_value


class TestUpdate(BaseManager, ReturnValueMixin):
    ID = 'repository-bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_package_repositories):
        with my_vcr.use_cassette("package_repositories/prepare_update_{}".format(self.ID)):
            repository = manager.get(self.ID)
        with my_vcr.use_cassette("package_repositories/update_{}".format(self.ID)) as cass:
            repository.data.name = 'updated-name'
            return cass, manager.update(repo_id=self.ID, repository=repository.data, etag=repository.etag)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/repositories/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self, manager):
        return 'PUT'

    @pytest.fixture()
    def expected_return_type(self):
        return package_repository.PackageRepository

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.name == 'updated-name'

        return check_value


class TestDelete(BaseManager, ReturnValueMixin):
    ID = 'repository-foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_package_repositories):
        with my_vcr.use_cassette("package_repositories/delete_{}".format(self.ID)) as cass:
            return cass, manager.delete(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/repositories/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result == "The package repository '{}' was deleted successfully.".format(self.ID)

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.package_repository.PackageRepositoryManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        repo_id = mock.MagicMock()
        _ = manager[repo_id]  # noqa
        get_mock.assert_called_once_with(repo_id=repo_id)

    @mock.patch('yagocd.resources.package_repository.PackageRepositoryManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
