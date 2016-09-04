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

import zlib
from six import string_types

from yagocd.resources import agent, job

import mock
import pytest


class BaseTestAgentManager(object):
    @pytest.fixture()
    def manager(self, session_fixture):
        return agent.AgentManager(session=session_fixture)

    @pytest.fixture()
    def first_agent_uuid(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/first_agent_uuid"):
            return manager.list()[0].data.uuid

    @staticmethod
    def _expected_accept_header(manager):
        if LooseVersion(manager._session.server_version) <= '16.1.0':
            return 'application/vnd.go.cd.v1+json'
        elif LooseVersion(manager._session.server_version) <= '16.3.0':
            return 'application/vnd.go.cd.v2+json'
        else:
            return 'application/vnd.go.cd.v3+json'


class TestCacheServerVersion(BaseTestAgentManager):
    def test_cache_server_version(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/server_version_cache"):
            assert manager._session.server_version


class TestListAsList(BaseTestAgentManager):
    def test_list_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list") as cass:
            manager.list()
            assert cass.requests[0].path == '/go/api/agents'

    def test_list_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list") as cass:
            manager.list()
            assert cass.requests[0].method == 'GET'

    def test_list_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list") as cass:
            manager.list()
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_list_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list") as cass:
            manager.list()
            assert cass.responses[0]['status']['code'] == 200

    def test_list_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.list()
            assert isinstance(result, list)

    def test_list_is_not_empty(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.list()
            assert len(result) > 0

    def test_list_returns_agent_entities(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.list()
            assert all(isinstance(i, agent.AgentEntity) for i in result)


class TestDict(BaseTestAgentManager):
    @mock.patch('yagocd.resources.agent.AgentManager.list')
    def test_dict_calls_list(self, mock_list, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            manager.dict()
            mock_list.assert_called()

    def test_dict_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.dict()
            assert isinstance(result, dict)

    def test_dict_returns_str_as_keys(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.dict()
            assert all(isinstance(i, string_types) for i in result.keys())

    def test_dict_returns_agent_entities_as_values(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.dict()
            assert all(isinstance(i, agent.AgentEntity) for i in result.values())

    def test_dict_get_by_key(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_list_as_list"):
            result = manager.dict().get(first_agent_uuid)
            assert result.data.uuid == first_agent_uuid


class TestGet(BaseTestAgentManager):
    def test_get_request_url(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_get") as cass:
            manager.get(first_agent_uuid)
            assert cass.requests[0].path == '/go/api/agents/{uuid}'.format(uuid=first_agent_uuid)

    def test_get_request_method(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_get") as cass:
            manager.get(first_agent_uuid)
            assert cass.requests[0].method == 'GET'

    def test_get_request_accept_headers(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_get") as cass:
            manager.get(first_agent_uuid)
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_get_response_code(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_get") as cass:
            manager.get(first_agent_uuid)
            assert cass.responses[0]['status']['code'] == 200

    def test_get_returns_instance_of_agent_entity(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_get"):
            result = manager.get(first_agent_uuid)
            assert isinstance(result, agent.AgentEntity)


class TestUpdate(BaseTestAgentManager):
    UPD_CFG = {'hostname': 'foo-bar'}

    def test_update_request_url(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update") as cass:
            manager.update(first_agent_uuid, self.UPD_CFG)
            assert cass.requests[0].path == '/go/api/agents/{uuid}'.format(uuid=first_agent_uuid)

    def test_update_request_method(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update") as cass:
            manager.update(first_agent_uuid, self.UPD_CFG)
            assert cass.requests[0].method == 'PATCH'

    def test_update_request_accept_headers(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update") as cass:
            manager.update(first_agent_uuid, self.UPD_CFG)
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_update_request_content_type_headers(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update") as cass:
            manager.update(first_agent_uuid, self.UPD_CFG)
            assert cass.requests[0].headers['content-type'] == 'application/json'

    def test_update_response_code(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update") as cass:
            manager.update(first_agent_uuid, self.UPD_CFG)
            assert cass.responses[0]['status']['code'] == 200

    def test_update_returns_instance_of_agent_entity(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update"):
            result = manager.update(first_agent_uuid, self.UPD_CFG)
            assert isinstance(result, agent.AgentEntity)

    def test_update_returns_updated_agent(self, manager, first_agent_uuid, my_vcr):
        with my_vcr.use_cassette("agent/agent_update"):
            result = manager.update(first_agent_uuid, self.UPD_CFG)
            assert result.data.hostname == self.UPD_CFG['hostname']


class TestDelete(BaseTestAgentManager):
    UUID = '964c760d-2803-4dac-a98e-6b3b2b682f3e'

    def test_delete_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_delete") as cass:
            manager.delete(self.UUID)
            assert cass.requests[0].path == '/go/api/agents/{uuid}'.format(uuid=self.UUID)

    def test_delete_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_delete") as cass:
            manager.delete(self.UUID)
            assert cass.requests[0].method == 'DELETE'

    def test_delete_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_delete") as cass:
            manager.delete(self.UUID)
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_delete_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_delete") as cass:
            manager.delete(self.UUID)
            assert cass.responses[0]['status']['code'] == 200

    def test_delete_return_message(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_delete") as cass:
            manager.delete(self.UUID)
            message = cass.responses[0]['body']['string']
            try:
                message = zlib.decompress(message, 16 + zlib.MAX_WBITS)
            except zlib.error:
                pass
            assert b'Deleted 1 agent(s)' in message


class TestJobHistory(BaseTestAgentManager):
    UUID = '6dae05c5-dc56-4bf4-95bc-af8badbe7be4'

    def test_job_history_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_job_history") as cass:
            manager.job_history(self.UUID)
            assert cass.requests[0].path == '/go/api/agents/{uuid}/job_run_history/{offset}'.format(
                uuid=self.UUID, offset=0
            )

    def test_job_history_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_job_history") as cass:
            manager.job_history(self.UUID)
            assert cass.requests[0].method == 'GET'

    def test_job_history_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_job_history") as cass:
            manager.job_history(self.UUID)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_job_history_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_job_history") as cass:
            manager.job_history(self.UUID)
            assert cass.responses[0]['status']['code'] == 200

    def test_job_history_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_job_history"):
            result = manager.job_history(self.UUID)
            assert isinstance(result, list)

    def test_job_history_returns_job_instances(self, manager, my_vcr):
        with my_vcr.use_cassette("agent/agent_job_history"):
            result = manager.job_history(self.UUID)
            assert all(isinstance(i, job.JobInstance) for i in result)
