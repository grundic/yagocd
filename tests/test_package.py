#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# The MIT License
#
# Copyright (c) 2017 Grigory Chernyshev
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
from yagocd.resources import package
from yagocd.resources import package_repository


@pytest.fixture()
def manager(session_fixture):
    return package.PackageManager(session=session_fixture)


@pytest.fixture()
def package_repository_manager(session_fixture):
    return package_repository.PackageRepositoryManager(session=session_fixture)


class BaseManager(AbstractTestManager):
    @pytest.fixture()
    def prepare_package_repository(self, package_repository_manager, my_vcr):
        with my_vcr.use_cassette("package/prepare_package_repo"):
            package_repository_manager.create(dict(
                repo_id='repository-for-package',
                name='repo.for.package',
                plugin_metadata=dict(id="yum", version="1"),
                configuration=[
                    dict(key="REPO_URL", value="http://package.example.com")
                ]
            ))

    @pytest.fixture()
    def prepare_packages(self, manager, my_vcr, prepare_package_repository):
        with my_vcr.use_cassette("package/prepare_packages"):
            manager.create(dict(
                id="package-foo",
                name="package.foo",
                auto_update=False,
                package_repo={
                    "id": "repository-for-package"
                },
                configuration=[
                    {
                        "key": "PACKAGE_SPEC",
                        "value": "This is a package FOO"
                    }
                ]
            ))

            manager.create(dict(
                id="package-bar",
                name="package.bar",
                auto_update=False,
                package_repo={
                    "id": "repository-for-package"
                },
                configuration=[
                    {
                        "key": "PACKAGE_SPEC",
                        "value": "This is a package BAR"
                    }
                ]
            ))


class TestList(BaseManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_packages):
        with my_vcr.use_cassette("package/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/packages'

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
            assert all(isinstance(i, package.Package) for i in result[0])

        return check_value


class TestGet(BaseManager, ReturnValueMixin):
    ID = 'package-foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_packages):
        with my_vcr.use_cassette("package/get_{}".format(self.ID)) as cass:
            return cass, manager.get(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/packages/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], package.Package)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.id == self.ID

        return check_value


class TestCreate(BaseManager, ReturnValueMixin):
    ID = 'repository-baz'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("package/create_{}".format(self.ID)) as cass:
            return cass, manager.create(dict(
                id=self.ID,
                name="package.baz",
                auto_update=False,
                package_repo={
                    "id": "repository-for-package"
                },
                configuration=[
                    {
                        "key": "PACKAGE_SPEC",
                        "value": "This is a package BAZ"
                    }
                ]
            ))

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/packages'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], package.Package)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.id == self.ID
            assert result[0].data.name == 'package.baz'

        return check_value


class TestUpdate(BaseManager, ReturnValueMixin):
    ID = 'package-bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_packages):
        with my_vcr.use_cassette("package/prepare_update_{}".format(self.ID)):
            package, etag = manager.get(self.ID)
        with my_vcr.use_cassette("package/update_{}".format(self.ID)) as cass:
            package.data.name = 'updated-name'
            return cass, manager.update(package_id=self.ID, package=package.data, etag=etag)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/packages/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self, manager):
        return 'PUT'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], package.Package)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.name == 'updated-name'

        return check_value


class TestDelete(BaseManager, ReturnValueMixin):
    ID = 'package-foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_packages):
        with my_vcr.use_cassette("package/delete_{}".format(self.ID)) as cass:
            return cass, manager.delete(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/packages/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result == "The package definition '{}' was deleted successfully.".format(self.ID)

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.package.PackageManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        package_id = mock.MagicMock()
        _ = manager[package_id]  # noqa
        get_mock.assert_called_once_with(package_id=package_id)

    @mock.patch('yagocd.resources.package.PackageManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
