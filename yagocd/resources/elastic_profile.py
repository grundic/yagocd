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

from yagocd.resources import Base, BaseManager
from yagocd.util import since


@since('16.11.0')
class ElasticAgentProfileManager(BaseManager):
    """
    The elastic agent profile API allows users with admin and group admin
    authorization to manage profiles that allow creation of elastic agents.

    `Official documentation. <https://api.go.cd/current/#elastic-agent-profiles>`_

    :versionadded: 16.11.0.
    """

    RESOURCE_PATH = '{base_api}/elastic/profiles'

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: list of yagocd.resources.elastic_profile.ElasticAgentProfile
        """
        return iter(self.list())

    def __getitem__(self, profile_id):
        """
        Method add possibility to get elastic agent by the name using dictionary like syntax.

        :param profile_id: id of the elastic profile to get the info.
        :rtype: yagocd.resources.elastic_profile.ElasticAgentProfile
        """
        return self.get(profile_id=profile_id)

    def list(self):
        """
        Lists all available elastic agent profiles.

        :rtype: list of yagocd.resources.elastic_profile.ElasticAgentProfile
        """
        response = self._session.get(
            path=self.RESOURCE_PATH.format(base_api=self.base_api)
        )

        result = list()
        etag = response.headers['ETag']
        for data in response.json().get('_embedded', {}).get('profiles', {}):
            result.append(ElasticAgentProfile(session=self._session, data=data, etag=etag))

        return result

    def get(self, profile_id):
        """
        Gets elastic agent profile config for specified profile.

        :param profile_id: id of the elastic agent profile to get.
        :rtype: yagocd.resources.elastic_profile.ElasticAgentProfile
        """
        response = self._session.get(
            path=self._session.urljoin(self.RESOURCE_PATH, profile_id).format(
                base_api=self.base_api
            )
        )

        etag = response.headers['ETag']
        return ElasticAgentProfile(session=self._session, data=response.json(), etag=etag)

    def create(self, config):
        """
        Creates an elastic agent profile.

        :param config: new elastic agent profile configuration.
        :rtype: yagocd.resources.elastic_profile.ElasticAgentProfile
        """
        response = self._session.post(
            path=self.RESOURCE_PATH.format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
            },
            data=json.dumps(config),
        )

        etag = response.headers['ETag']
        return ElasticAgentProfile(session=self._session, data=response.json(), etag=etag)

    def update(self, profile_id, profile, etag):
        """
        Update some attributes of an elastic agent profile.

        :param profile_id: id of the elastic profile to update.
        :param profile: updated agent profile configuration.
        :param etag: etag value from current agent profile.
        :rtype: yagocd.resources.elastic_profile.ElasticAgentProfile
        """

        response = self._session.put(
            path=self._session.urljoin(self.RESOURCE_PATH, profile_id).format(
                base_api=self.base_api
            ),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
            data=json.dumps(profile),
        )

        etag = response.headers['ETag']
        return ElasticAgentProfile(session=self._session, data=response.json(), etag=etag)

    def delete(self, profile_id):
        """
        Deletes the profile.

        :param profile_id: id of the elastic profile to delete.
        :return: a message if the elastic agent profile is deleted or not.
        :rtype: str
        """

        response = self._session.delete(
            path=self._session.urljoin(self.RESOURCE_PATH, profile_id).format(
                base_api=self.base_api
            ),
            headers={
                'Accept': self._accept_header(),
            },
        )

        return response.json().get('message')


class ElasticAgentProfile(Base):
    pass
