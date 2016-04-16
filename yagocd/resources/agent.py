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
    ACCEPT_HEADER = 'application/vnd.go.cd.v2+json'

    def list(self):
        response = self._session.get(
            path='{base_api}/agents'.format(base_api=self.base_api),
            headers={'Accept': self.ACCEPT_HEADER},
        )

        agents = list()
        for data in response.json().get('_embedded', {}).get('agents', {}):
            agents.append(AgentEntity(session=self._session, data=data))

        return agents

    def get(self, uuid):
        """
        Gets an agent by its unique identifier (uuid).

        :param uuid: uuid of the agent
        :return: Agent entity.
        """
        response = self._session.get(
            path='{base_api}/agents/{uuid}'.format(
                base_api=self.base_api,
                uuid=uuid,
            ),
            headers={'Accept': self.ACCEPT_HEADER},
        )

        return AgentEntity(session=self._session, data=response.json())

    def update(self, uuid, config):
        """
        Update some attributes of an agent.

        :param uuid: uuid of the agent
        :param config: dictionary of parameters for update
        :return: Agent entity.
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


if __name__ == '__main__':
    pass
