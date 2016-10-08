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
class SCMManager(BaseManager):
    """
    The pluggable SCM API allows users to view, create and update the SCM object.

    `Official documentation. <https://api.go.cd/current/#scms>`_

    :note: Please keep in mind that this API works with pluggable SCM materials,
     which means that you have to install specific SCM plugin to the GoCD server
     in order to work with it.

    :versionadded: 16.7.0.
    """

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: (list of yagocd.resources.scm.SCMMaterial, str)
        """
        return iter(self.list()[0])

    def __getitem__(self, name):
        """
        Method add possibility to get SCM material by the name using dictionary like syntax.

        :param name: scm material name.
        :rtype: (yagocd.resources.scm.SCMMaterial, str)
        """
        return self.get(name=name)

    def list(self):
        """
        Lists all available pluggable scm materials,
        these are materials that are present in the in ``cruise-config.xml``.

        :rtype: (list of yagocd.resources.scm.SCMMaterial, str)
        """
        response = self._session.get(
            path='{base_api}/admin/scms'.format(base_api=self.base_api)
        )

        result = list()
        for data in response.json().get('_embedded', {}).get('scms', {}):
            result.append(SCMMaterial(session=self._session, data=data))

        etag = response.headers['ETag']
        return result, etag

    def get(self, name):
        """
        Gets pluggable scm material for a specified scm name.

        :param name: scm material name.
        :rtype: (yagocd.resources.scm.SCMMaterial, str)
        """
        response = self._session.get(
            path='{base_api}/admin/scms/{name}'.format(
                base_api=self.base_api, name=name,
            ),
        )

        etag = response.headers['ETag']
        return SCMMaterial(session=self._session, data=response.json()), etag

    def create(self, config):
        """
        Create a global SCM object.

        :param config: new SCM configuration.
        :rtype: (yagocd.resources.scm.SCMMaterial, str)
        """
        response = self._session.post(
            path='{base_api}/admin/scms'.format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
            },
            data=json.dumps(config),
        )

        etag = response.headers['ETag']
        return SCMMaterial(session=self._session, data=response.json()), etag

    def update(self, name, config, etag):
        """
        Update some attributes of SCM material.

        :param name: name of SCM material to update.
        :param config: updated SCM material configuration.
        :param etag: etag value from current SCM material.
        :rtype: (yagocd.resources.scm.SCMMaterial, str)
        """
        api_method = self._session.put
        if LooseVersion(self._session.server_version) <= LooseVersion('16.9.0'):
            api_method = self._session.patch

        response = api_method(
            path='{base_api}/admin/scms/{name}'.format(
                base_api=self.base_api, name=name),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
            data=json.dumps(config),
        )

        etag = response.headers['ETag']
        return SCMMaterial(session=self._session, data=response.json()), etag


class SCMMaterial(Base):
    pass
