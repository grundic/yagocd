#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# The MIT License
#
# Copyright (c) 2017 Grigory Chernyshev
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


@since('16.12.0')
class PackageManager(BaseManager):
    """
    The package definition API allows users to view, create and update the packages’ configuration.

    `Official documentation. <https://api.go.cd/current/#packages>`_

    :versionadded: 16.12.0.
    """

    RESOURCE_PATH = '{base_api}/admin/packages'

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: list of yagocd.resources.package.Package
        """
        return iter(self.list())

    def __getitem__(self, package_id):
        """
        Method add possibility to get package by the name using dictionary like syntax.

        :param package_id: id of the package to get.
        :rtype: yagocd.resources.package.Package
        """
        return self.get(package_id=package_id)

    def list(self):  # noqa
        """
        Lists all available packages, these are materials that are present in the in cruise-config.xml.

        :rtype: list of yagocd.resources.package.Package
        """
        response = self._session.get(
            path=self.RESOURCE_PATH.format(base_api=self.base_api)
        )

        result = list()
        etag = response.headers['ETag']
        for data in response.json().get('_embedded', {}).get('packages', {}):
            result.append(Package(session=self._session, data=data, etag=etag))

        return result

    def get(self, package_id):
        """
        Gets the package config for a specified package id.

        :param package_id: id of the package to get.
        :rtype: yagocd.resources.package.Package
        """
        response = self._session.get(
            path=self._session.urljoin(self.RESOURCE_PATH, package_id).format(base_api=self.base_api)
        )

        etag = response.headers['ETag']

        return Package(session=self._session, data=response.json(), etag=etag)

    def create(self, config):
        """
        Creates a package with specified configurations.

        :param config: new package configuration.
        :rtype: yagocd.resources.package.Package
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
        return Package(session=self._session, data=response.json(), etag=etag)

    def update(self, package_id, package, etag):
        """
        Updates global package configuration for the specified package id.

        :param package_id: id of the package repository to update.
        :param package: updated package configuration.
        :param etag: etag value from current package repository.
        :rtype: yagocd.resources.package.Package
        """

        response = self._session.put(
            path=self._session.urljoin(self.RESOURCE_PATH, package_id).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
            data=json.dumps(package),
        )

        etag = response.headers['ETag']
        return Package(session=self._session, data=response.json(), etag=etag)

    def delete(self, package_id):
        """
        Deletes a package from the respective repository if it is not associated with any pipeline.

        :param package_id: id of the package repository to delete.
        :return: a message if the package repository is deleted or not.
        :rtype: str
        """

        response = self._session.delete(
            path=self._session.urljoin(self.RESOURCE_PATH, package_id).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
            },
        )

        return response.json().get('message')


class Package(Base):
    pass
