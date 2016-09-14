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

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import plugin_info


@pytest.fixture()
def manager(session_fixture):
    return plugin_info.PluginInfoManager(session=session_fixture)


class TestList(AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("plugin_info/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/plugin_info'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self, gocd_docker):
        def check_value(result):
            assert all(isinstance(i, plugin_info.PluginInfo) for i in result)

        return check_value


class TestGet(AbstractTestManager, ReturnValueMixin):
    NAME = 'yum'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("plugin_info/get_{}".format(self.NAME)) as cass:
            return cass, manager.get(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/plugin_info/{name}'.format(name=self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return plugin_info.PluginInfo

    @pytest.fixture()
    def expected_return_value(self, gocd_docker):
        def check_value(result):
            assert result.data.id == self.NAME

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.plugin_info.PluginInfoManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        name = mock.MagicMock()
        _ = manager[name]  # noqa
        get_mock.assert_called_once_with(name=name)

    @mock.patch('yagocd.resources.plugin_info.PluginInfoManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
