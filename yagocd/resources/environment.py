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
from distutils.version import LooseVersion

from yagocd.resources import Base, BaseManager
from yagocd.util import since


@since('16.7.0')
class EnvironmentManager(BaseManager):
    """
    The environment config API allows users with administrator role
    to manage environment config.

    `Official documentation. <https://api.go.cd/current/#environment-config>`_

    :versionadded: 16.7.0.
    """

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: (list of yagocd.resources.environment.EnvironmentConfig, str)
        """
        return iter(self.list()[0])

    def __getitem__(self, name):
        """
        Method add possibility to get environment by the name using dictionary like syntax.

        :param name: name of the environment to fetch.
        :rtype: (yagocd.resources.environment.EnvironmentConfig, str)
        """
        return self.get(name=name)

    def list(self):
        """
        Lists all available environments.

        :rtype: (list of yagocd.resources.environment.EnvironmentConfig, str)
        """
        response = self._session.get(
            path='{base_api}/admin/environments'.format(base_api=self.base_api)
        )

        result = list()
        for data in response.json().get('_embedded', {}).get('environments', {}):
            result.append(EnvironmentConfig(session=self._session, data=data))

        etag = response.headers['ETag']
        return result, etag

    def get(self, name):
        """
        Gets environment by the given name.

        :param name: name of the environment to fetch.
        :rtype: (yagocd.resources.environment.EnvironmentConfig, str)
        """
        response = self._session.get(
            path='{base_api}/admin/environments/{name}'.format(
                base_api=self.base_api, name=name
            )
        )

        etag = response.headers['ETag']
        return EnvironmentConfig(session=self._session, data=response.json()), etag

    def create(self, config):
        """
        Creates an environment.

        :param config: new environment configuration.
        :rtype: (yagocd.resources.environment.EnvironmentConfig, str)
        """
        response = self._session.post(
            path='{base_api}/admin/environments'.format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
            },
            data=json.dumps(config),
        )

        etag = response.headers['ETag']
        return EnvironmentConfig(session=self._session, data=response.json()), etag

    def update(self, name, config, etag):
        """
        Update some attributes of an environment.

        :param name: name of environment to update.
        :param config: updated environment configuration.
        :param etag: etag value from current environment resource.
        :rtype: (yagocd.resources.environment.EnvironmentConfig, str)
        """

        api_method = self._session.put
        if LooseVersion(self._session.server_version) <= LooseVersion('16.9.0'):
            api_method = self._session.patch

        response = api_method(
            path='{base_api}/admin/environments/{name}'.format(
                base_api=self.base_api, name=name),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
            data=json.dumps(config),
        )

        etag = response.headers['ETag']
        return EnvironmentConfig(session=self._session, data=response.json()), etag

    def delete(self, name):
        """
        Deletes an environment.

        :param name: name of the environment to fetch.
        :return: A message confirmation if the environment was deleted.
        :rtype: str
        """
        response = self._session.delete(
            path='{base_api}/admin/environments/{name}'.format(
                base_api=self.base_api, name=name
            )
        )

        return response.json().get('message')


class EnvironmentConfig(Base):
    pass
