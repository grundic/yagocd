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
import json
import os
from distutils.version import LooseVersion

import pytest
from mock import mock

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import scm


@pytest.fixture()
def manager(session_fixture):
    return scm.SCMManager(session=session_fixture)


class BaseManager(AbstractTestManager):
    @pytest.fixture()
    def scm_material_foo(self, tests_dir):
        path = os.path.join(tests_dir, 'fixtures/resources/scm/scm-material-foo.json')
        return json.load(open(path))

    @pytest.fixture()
    def scm_material_bar(self, tests_dir):
        path = os.path.join(tests_dir, 'fixtures/resources/scm/scm-material-bar.json')
        return json.load(open(path))

    @pytest.fixture()
    def scm_material_baz(self, tests_dir):
        path = os.path.join(tests_dir, 'fixtures/resources/scm/scm-material-baz.json')
        return json.load(open(path))

    @pytest.fixture()
    def prepare_scm_material(self, manager, my_vcr, scm_material_foo, scm_material_bar):
        with my_vcr.use_cassette("scm/prepare"):
            manager.create(config=scm_material_foo)
            manager.create(config=scm_material_bar)


class TestList(BaseManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_scm_material):
        with my_vcr.use_cassette("scm/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/scms'

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
            assert all(isinstance(i, scm.SCMMaterial) for i in result[0])

        return check_value


class TestGet(BaseManager, ReturnValueMixin):
    NAME = 'bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_scm_material):
        with my_vcr.use_cassette("scm/get_{}".format(self.NAME)) as cass:
            return cass, manager.get(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/scms/{}'.format(self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], scm.SCMMaterial)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.name == self.NAME
            assert result[0].data.id == "scm-id-bar"

        return check_value


class TestCreate(BaseManager, ReturnValueMixin):
    NAME = 'baz'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, scm_material_baz):
        with my_vcr.use_cassette("scm/create_{}".format(self.NAME)) as cass:
            return cass, manager.create(config=scm_material_baz)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/scms'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], scm.SCMMaterial)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.name == self.NAME
            assert result[0].data.id == "scm-id-baz"

        return check_value


class TestUpdate(BaseManager, ReturnValueMixin):
    NAME = 'bar'
    NEW_VALUE = 'NEW-DUMMY-VALUE'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_scm_material, scm_material_bar):
        with my_vcr.use_cassette("scm/prepare_update_{}".format(self.NAME)):
            _, etag = manager.get(self.NAME)  # noqa
        with my_vcr.use_cassette("scm/update_{}".format(self.NAME)) as cass:
            scm_material_bar['configuration'][0]['value'] = self.NEW_VALUE
            return cass, manager.update(
                name=self.NAME,
                config=scm_material_bar,
                etag=etag
            )

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/scms/{}'.format(self.NAME)

    @pytest.fixture()
    def expected_request_method(self, manager):
        if LooseVersion(manager._session.server_version) <= LooseVersion('16.9.0'):
            return 'PATCH'
        return 'PUT'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], scm.SCMMaterial)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.configuration[0].value == self.NEW_VALUE

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.scm.SCMManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        name = mock.MagicMock()
        _ = manager[name]  # noqa
        get_mock.assert_called_once_with(name=name)

    @mock.patch('yagocd.resources.scm.SCMManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
