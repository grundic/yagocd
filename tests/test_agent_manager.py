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

import mock
import pytest
from six import string_types

from tests import AbstractTestManager, RequestContentTypeHeadersMixin, ReturnValueMixin
from yagocd.resources import agent, job


@pytest.fixture()
def manager(session_fixture):
    return agent.AgentManager(session=session_fixture)


class BaseTestAgentManager(AbstractTestManager):
    @pytest.fixture()
    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def _execute_test_action(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def first_agent_uuid(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/first_agent_uuid"):
            return manager.list()[0].data.uuid

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        if LooseVersion(server_version) <= LooseVersion('16.1.0'):
            return 'application/vnd.go.cd.v1+json'
        elif LooseVersion(server_version) <= LooseVersion('16.7.0'):
            return 'application/vnd.go.cd.v2+json'
        elif LooseVersion(server_version) <= LooseVersion('16.9.0'):
            return 'application/vnd.go.cd.v3+json'
        else:
            return 'application/vnd.go.cd.v4+json'


class TestListAsList(BaseTestAgentManager, ReturnValueMixin):
    TEST_METHOD_NAME = 'list'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/agents'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            len(result) > 0
            assert all(isinstance(i, agent.AgentEntity) for i in result)

        return check_value


class TestDict(TestListAsList):
    TEST_METHOD_NAME = 'dict'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list") as cass:
            return cass, manager.dict()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/agents'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return dict

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert len(result) > 0
            assert all(isinstance(i, string_types) for i in result.keys())
            assert all(isinstance(i, agent.AgentEntity) for i in result.values())

        return check_value

    @mock.patch('yagocd.resources.agent.AgentManager.list')
    def test_list_method_is_called(self, mock_list, manager, my_vcr):
        self._execute_test_action(manager, my_vcr)
        mock_list.assert_called()

    def test_dict_get_by_key(self, _execute_test_action, first_agent_uuid):
        cass, result = _execute_test_action
        first_agent = result.get(first_agent_uuid)
        assert first_agent.data.uuid == first_agent_uuid


class TestGet(BaseTestAgentManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, first_agent_uuid):
        with my_vcr.use_cassette("agent/agent_get") as cass:
            return cass, manager.get(first_agent_uuid)

    @pytest.fixture()
    def expected_request_url(self, first_agent_uuid):
        return '/go/api/agents/{uuid}'.format(uuid=first_agent_uuid)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return agent.AgentEntity

    @pytest.fixture()
    def expected_return_value(self, first_agent_uuid):
        def check_value(result):
            assert result.data.uuid == first_agent_uuid

        return check_value


class TestUpdate(BaseTestAgentManager, RequestContentTypeHeadersMixin, ReturnValueMixin):
    UPD_CFG = {'hostname': 'foo-bar'}

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, first_agent_uuid):
        with my_vcr.use_cassette("agent/agent_update") as cass:
            return cass, manager.update(first_agent_uuid, self.UPD_CFG)

    @pytest.fixture()
    def expected_request_url(self, first_agent_uuid):
        return '/go/api/agents/{uuid}'.format(uuid=first_agent_uuid)

    @pytest.fixture()
    def expected_request_method(self):
        return 'PATCH'

    @pytest.fixture()
    def expected_content_type_headers(self, *args, **kwargs):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return agent.AgentEntity

    @pytest.fixture()
    def expected_return_value(self, first_agent_uuid):
        def check_value(result):
            assert result.data.hostname == self.UPD_CFG['hostname']

        return check_value


class TestDelete(BaseTestAgentManager, ReturnValueMixin):
    UUID = '964c760d-2803-4dac-a98e-6b3b2b682f3e'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, first_agent_uuid):
        with my_vcr.use_cassette("agent/agent_delete") as cass:
            return cass, manager.delete(self.UUID)

    @pytest.fixture()
    def expected_request_url(self, first_agent_uuid):
        return '/go/api/agents/{uuid}'.format(uuid=self.UUID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self, first_agent_uuid):
        def check_value(result):
            assert 'Deleted 1 agent(s)' in result

        return check_value


class TestJobHistory(BaseTestAgentManager, ReturnValueMixin):
    UUID = '6dae05c5-dc56-4bf4-95bc-af8badbe7be4'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, first_agent_uuid):
        with my_vcr.use_cassette("agent/agent_job_history") as cass:
            return cass, manager.job_history(self.UUID)

    @pytest.fixture()
    def expected_request_url(self, first_agent_uuid):
        return '/go/api/agents/{uuid}/job_run_history/{offset}'.format(
            uuid=self.UUID, offset=0
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self, first_agent_uuid):
        def check_value(result):
            assert all(isinstance(i, job.JobInstance) for i in result)

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.agent.AgentManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        uuid = mock.MagicMock()
        _ = manager[uuid]  # noqa
        get_mock.assert_called_once_with(uuid=uuid)

    @mock.patch('yagocd.resources.agent.AgentManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
