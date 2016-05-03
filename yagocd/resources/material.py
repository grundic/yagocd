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

from yagocd.resources import BaseManager, Base


class MaterialManager(BaseManager):
    """
    The materials API allows users to query and notify materials in the Go configuration.
    """

    def list(self):
        """
        Lists all available materials, these are materials that are present in the in ``cruise-config.xml``.
        :return: An array of :class:`yagocd.resources.material.MaterialEntity`.
        :rtype: list of yagocd.resources.material.MaterialEntity
        """
        response = self._session.get(
            path='{base_api}/config/materials'.format(base_api=self.base_api),
            headers={'Accept': 'application/json'},
        )

        materials = list()
        for data in response.json():
            materials.append(MaterialEntity(session=self._session, data=data))

        return materials

    def modifications(self, fingerprint, offset=0):
        """
        Get modifications of specific material.

        :param fingerprint: fingerprint of material.
        :param offset: number of modifications to be skipped.
        :return: A list of modification objects :class:`yagocd.resources.material.ModificationEntity`.
        :rtype: list of yagocd.resources.material.ModificationEntity
        """
        response = self._session.get(
            path='{base_api}/materials/{fingerprint}/modifications/{offset}'.format(
                base_api=self.base_api,
                fingerprint=fingerprint,
                offset=offset
            ),
            headers={'Accept': 'application/json'},
        )

        modifications = list()
        for data in response.json().get('modifications', {}):
            modifications.append(ModificationEntity(session=self._session, data=data))

        return modifications

    def notify_svn(self, uuid):
        """
        APIs that notify Go Server when a commit has been made in Version Control
        and Go needs to trigger relevant pipelines.

        [!!!] When using this feature, uncheck Poll for new changes or
        set autoUpdate flag in cruise configuration to false for the relevant material.
        Otherwise you will get:
           requests.exceptions.HTTPError: 404 Client Error:
           Not Found for url: http://localhost:8153/go/api/material/notify/svn

        :param uuid: The subversion repository UUID.
        :return: A text confirmation.
        """
        response = self._session.post(
            path='{base_api}/material/notify/svn'.format(base_api=self.base_api),
            data={'uuid': uuid},
            headers={
                'Accept': 'application/json'
            },
        )

        return response.text

    def notify_git(self, url):
        """
        APIs that notify Go Server when a commit has been made in Version Control
        and Go needs to trigger relevant pipelines.

        [!!!] When using this feature, uncheck Poll for new changes or
        set autoUpdate flag in cruise configuration to false for the relevant material.
        Otherwise you will get:
           requests.exceptions.HTTPError: 404 Client Error:
           Not Found for url: http://localhost:8153/go/api/material/notify/git

        :param url: The git repository url as defined in cruise-config.xml.
        :return: A text confirmation.
        """
        response = self._session.post(
            path='{base_api}/material/notify/git'.format(base_api=self.base_api),
            data={'repository_url': url},
            headers={
                'Accept': 'application/json'
            },
        )

        return response.text

    def notify_hg(self, url):
        """
        APIs that notify Go Server when a commit has been made in Version Control
        and Go needs to trigger relevant pipelines.

        [!!!] When using this feature, uncheck Poll for new changes or
        set autoUpdate flag in cruise configuration to false for the relevant material.
        Otherwise you will get:
           requests.exceptions.HTTPError: 404 Client Error:
           Not Found for url: http://localhost:8153/go/api/material/notify/hg

        :param url: The git repository url as defined in cruise-config.xml.
        :return: A text confirmation.
        """
        response = self._session.post(
            path='{base_api}/material/notify/hg'.format(base_api=self.base_api),
            data={'repository_url': url},
            headers={
                'Accept': 'application/json'
            },
        )

        return response.text


class MaterialEntity(Base):
    pass


class ModificationEntity(Base):
    pass
