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
from yagocd.resources import elastic_profile


@pytest.fixture()
def manager(session_fixture):
    return elastic_profile.ElasticAgentProfileManager(session=session_fixture)


class BaseManager(AbstractTestManager):
    @pytest.fixture()
    def prepare_agent_profiles(self, manager, my_vcr):
        with my_vcr.use_cassette("elastic_profile/prepare"):
            manager.create({
                "id": "foo",
                "plugin_id": "cd.go.contrib.elastic-agent.docker",
                "properties": [
                    {"key": "Image", "value": "gocdcontrib/gocd-dev-build"},
                    {"key": "Environment", "value": "JAVA_HOME=/opt/java\nMAKE_OPTS=-j8"}
                ]
            })

            manager.create({
                "id": "bar",
                "plugin_id": "cd.go.contrib.elastic-agent.docker",
                "properties": [
                    {"key": "mykey", "value": "myvalue"},
                    {"key": "another-key", "value": "hello-value"}
                ]
            })


class TestList(BaseManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_agent_profiles):
        with my_vcr.use_cassette("elastic_profile/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/elastic/profiles'

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
            assert all(isinstance(i, elastic_profile.ElasticAgentProfile) for i in result[0])

        return check_value


class TestGet(BaseManager, ReturnValueMixin):
    ID = 'foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_agent_profiles):
        with my_vcr.use_cassette("elastic_profile/get_{}".format(self.ID)) as cass:
            return cass, manager.get(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/elastic/profiles/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], elastic_profile.ElasticAgentProfile)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.id == self.ID

        return check_value


class TestCreate(BaseManager, ReturnValueMixin):
    ID = 'baz'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("elastic_profile/create_{}".format(self.ID)) as cass:
            return cass, manager.create(dict(
                id=self.ID,
                plugin_id="cd.go.contrib.elastic-agent.docker",
                properties=[{"key": "foo", "value": "bar"}]
            ))

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/elastic/profiles'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], elastic_profile.ElasticAgentProfile)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.id == self.ID
            assert result[0].data.properties[0].key == 'foo'
            assert result[0].data.properties[0].value == 'bar'

        return check_value


class TestUpdate(BaseManager, ReturnValueMixin):
    ID = 'bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_agent_profiles):
        with my_vcr.use_cassette("elastic_profile/prepare_update_{}".format(self.ID)):
            profile, etag = manager.get(self.ID)
        with my_vcr.use_cassette("elastic_profile/update_{}".format(self.ID)) as cass:
            profile.data.properties[1]['value'] = 'updated-value'
            return cass, manager.update(profile_id=self.ID, profile=profile.data, etag=etag)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/elastic/profiles/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self, manager):
        return 'PUT'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], elastic_profile.ElasticAgentProfile)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result[0].data.properties[1]['value'] == 'updated-value'

        return check_value


class TestDelete(BaseManager, ReturnValueMixin):
    ID = 'foo'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_agent_profiles):
        with my_vcr.use_cassette("elastic_profile/delete_{}".format(self.ID)) as cass:
            return cass, manager.delete(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/elastic/profiles/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result == "The elastic agent profile '{}' was deleted successfully.".format(self.ID)

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.elastic_profile.ElasticAgentProfileManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        profile_id = mock.MagicMock()
        _ = manager[profile_id]  # noqa
        get_mock.assert_called_once_with(profile_id=profile_id)

    @mock.patch('yagocd.resources.elastic_profile.ElasticAgentProfileManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
