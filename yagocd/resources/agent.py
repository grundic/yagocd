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

from yagocd.resources import BaseManager, Base
from yagocd.resources.job import JobInstance


class AgentManager(BaseManager):
    """
    The agents API allows users with administrator role to manage agents.

    :warning: Please note that this API requires using v2 of the API using `Accept: application/vnd.go.cd.v2+json`
    """

    # Using this header is actually impossible, as it doesn't work as documented in most cases...
    ACCEPT_HEADER = 'application/vnd.go.cd.v2+json'

    def list(self):
        """
        Lists all available agents, these are agents that are present in the
        <agents/> tag inside cruise-config.xml and also agents that are in
        Pending state awaiting registration.

        :return: an array of agents.
        :rtype: list of yagocd.resources.agent.AgentEntity
        """
        response = self._session.get(
            path='{base_api}/agents'.format(base_api=self.base_api),
            headers={'Accept': self.ACCEPT_HEADER},
        )

        agents = list()
        # Depending on Go version, return value would be either list of dict.
        # Support both cases here.
        json_response = response.json()
        if isinstance(json_response, list):
            agents_json = json_response
        elif isinstance(json_response, dict):
            agents_json = json_response.get('_embedded', {}).get('agents', {})
        else:
            raise ValueError("Expected response to be in [list, dict], but '{}' found!".format(json_response))

        for data in agents_json:
            agents.append(AgentEntity(session=self._session, data=data))

        return agents

    def dict(self):
        """
        Wrapper for `list()` method, that transforms founded agents to
        dictionary by `uuid` key.

        :return: dictionary of agents with `uuid` as a key and agent as a value.
        :rtype: dict[str, yagocd.resources.agent.AgentEntity]
        """
        agents = self.list()
        result = dict()
        for agent in agents:
            result[agent.data.uuid] = agent

        return result

    def get(self, uuid):
        """
        Gets an agent by its unique identifier (uuid).

        :param uuid: uuid of the agent
        :return: Agent entity.
        :rtype: yagocd.resources.agent.AgentEntity
        """
        response = self._session.get(
            path='{base_api}/agents/{uuid}'.format(
                base_api=self.base_api,
                uuid=uuid,
            ),
            # and again, WTF?!!
            # This depends on Go version: v2 works for later version of Go (16), but doesn't for earlier (15).
            # And because there is no good way to get version of the Go server (WTF?!), just use v1 header for now.
            # headers={'Accept': self.ACCEPT_HEADER},
        )

        return AgentEntity(session=self._session, data=response.json())

    def update(self, uuid, config):
        """
        Update some attributes of an agent.

        :param uuid: uuid of the agent
        :param config: dictionary of parameters for update
        :return: Agent entity.
        :rtype: yagocd.resources.agent.AgentEntity
        """
        response = self._session.patch(
            path='{base_api}/agents/{uuid}'.format(
                base_api=self.base_api,
                uuid=uuid,
            ),
            data=json.dumps(config),
            headers={
                # 'Accept': self.ACCEPT_HEADER,  # WTF?!!
                'Content-Type': 'application/json'
            },
        )

        return AgentEntity(session=self._session, data=response.json())

    def delete(self, uuid):
        """
        Deletes an agent.

        :param uuid: uuid of the agent.
        :return: a message confirmation if the agent was deleted.
        """
        response = self._session.delete(
            path='{base_api}/agents/{uuid}'.format(
                base_api=self.base_api,
                uuid=uuid,
            ),
            # headers={'Accept': self.ACCEPT_HEADER},  # WTF?!!
        )

        return response.json().get('message')

    def job_history(self, uuid, offset=0):
        """
        Lists the jobs that have executed on an agent.

        :param uuid: uuid of the agent.
        :param offset: number of jobs to be skipped.
        :return: an array of :class:`yagocd.resources.job.JobInstance` along with the job transitions.
        :rtype: list of yagocd.resources.job.JobInstance
        """
        response = self._session.get(
            path='{base_api}/agents/{uuid}/job_run_history/{offset}'.format(
                base_api=self.base_api,
                uuid=uuid,
                offset=offset
            ),
            headers={'Accept': self.ACCEPT_HEADER},
        )

        jobs = list()
        for data in response.json()['jobs']:
            jobs.append(JobInstance(session=self._session, data=data, stage=None))
        return jobs


class AgentEntity(Base):
    pass
