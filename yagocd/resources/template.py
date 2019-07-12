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


@since('16.10.0')
class TemplateManager(BaseManager):
    """
    The template config API allows users with administrator role to manage template config.

    `Official documentation. <https://api.go.cd/current/#template-config>`_

    :versionadded: 16.10.0.
    """

    RESOURCE_PATH = '{base_api}/admin/templates'

    ACCEPT_HEADER = 'application/vnd.go.cd.v3+json'

    VERSION_TO_ACCEPT_HEADER = {
        '16.10.0': 'application/vnd.go.cd.v1+json',
        '16.11.0': 'application/vnd.go.cd.v2+json',
    }

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: list of yagocd.resources.template.TemplateConfig
        """
        return iter(self.list())

    def __getitem__(self, name):
        """
        Method add possibility to get template by the name using dictionary like syntax.

        :param name: template name.
        :rtype: yagocd.resources.template.TemplateConfig
        """
        return self.get(name=name)

    def list(self):  # noqa
        """
        Lists all available templates with the associated pipelines’ names.

        :rtype: list of yagocd.resources.template.TemplateConfig
        """
        response = self._session.get(
            path=self.RESOURCE_PATH.format(base_api=self.base_api),
            headers={'Accept': self._accept_header()}
        )

        result = list()

        data_source = response.json()
        if LooseVersion(self._session.server_version) >= LooseVersion('16.11.0'):
            data_source = data_source.get('_embedded', {})

        etag = response.headers['ETag']
        for data in data_source.get('templates', {}):
            result.append(TemplateConfig(session=self._session, data=data, etag=etag))

        return result

    def get(self, name):
        """
        Gets template config for specified template name.

        :param name: name of the template.
        :rtype: yagocd.resources.template.TemplateConfig
        """
        response = self._session.get(
            path=self._session.urljoin(self.RESOURCE_PATH, name).format(base_api=self.base_api),
            headers={'Accept': self._accept_header()}
        )

        etag = response.headers['ETag']
        return TemplateConfig(session=self._session, data=response.json(), etag=etag)

    def create(self, config):
        """
        Creates a template config object.

        :param config: new template configuration.
        :rtype: yagocd.resources.template.TemplateConfig
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
        return TemplateConfig(session=self._session, data=response.json(), etag=etag)

    def update(self, name, config, etag):
        """
        Update template config for specified template name.

        :param name: name of the template to update.
        :param config: updated template configuration.
        :param etag: etag value from current template object.
        :rtype: yagocd.resources.template.TemplateConfig
        """
        response = self._session.put(
            path=self._session.urljoin(self.RESOURCE_PATH, name).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
            data=json.dumps(config),
        )

        etag = response.headers['ETag']
        return TemplateConfig(session=self._session, data=response.json(), etag=etag)

    def delete(self, name):
        """
        Deletes a template from the config XML if it is not associated with any pipeline.

        :param name: name of template to delete
        :return: A message confirmation if the template was deleted.
        :rtype: str
        """

        response = self._session.delete(
            path=self._session.urljoin(self.RESOURCE_PATH, name).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
            },
        )

        return response.json().get('message')


class TemplateConfig(Base):
    pass
