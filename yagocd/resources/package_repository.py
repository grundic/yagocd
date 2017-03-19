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


@since('16.12.0')
class PackageRepositoryManager(BaseManager):
    """
    The repositories API allows admins and pipeline group admins to view, create and update a package repository.

    `Official documentation. <https://api.go.cd/current/#package-repositories>`_

    :versionadded: 16.12.0.
    """

    RESOURCE_PATH = '{base_api}/admin/repositories'

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: list of yagocd.resources.package_repository.PackageRepository
        """
        return iter(self.list())

    def __getitem__(self, repo_id):
        """
        Method add possibility to get package repository by the name using dictionary like syntax.

        :param repo_id: id of the package repository to get the info.
        :rtype: yagocd.resources.package_repository.PackageRepository
        """
        return self.get(repo_id=repo_id)

    def list(self):
        """
        Lists all available package repositories in cruise-config.xml.

        :rtype: (list of yagocd.resources.package_repository.PackageRepository, str)
        """
        response = self._session.get(
            path=self.RESOURCE_PATH.format(base_api=self.base_api)
        )

        result = list()
        for data in response.json().get('_embedded', {}).get('package_repositories', {}):
            result.append(PackageRepository(session=self._session, data=data))

        etag = response.headers['ETag']

        return result, etag

    def get(self, repo_id):
        """
        Get a repository for a specified id.

        :param repo_id: id of the package repository to get.
        :rtype: (yagocd.resources.package_repository.PackageRepository, str)
        """
        response = self._session.get(
            path=self._session.urljoin(self.RESOURCE_PATH, repo_id).format(base_api=self.base_api)
        )

        etag = response.headers['ETag']

        return PackageRepository(session=self._session, data=response.json()), etag

    def create(self, config):
        """
        Create the repository configuration in cruise-config.xml.

        :param config: new package repository configuration.
        :rtype: (yagocd.resources.package_repository.PackageRepository, str)
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
        return PackageRepository(session=self._session, data=response.json()), etag

    def update(self, repo_id, repository, etag):
        """
        Update package repository for specified repository id.

        :param repo_id: id of the package repository to update.
        :param repository: updated package repository configuration.
        :param etag: etag value from current package repository.
        :rtype: (yagocd.resources.package_repository.PackageRepository, str)
        """

        response = self._session.put(
            self._session.urljoin(self.RESOURCE_PATH, repo_id).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
            data=json.dumps(repository),
        )

        etag = response.headers['ETag']
        return PackageRepository(session=self._session, data=response.json()), etag

    def delete(self, repo_id):
        """
        Deletes a package repository from the config XML if its packages are not associated with any pipeline.

        :param repo_id: id of the package repository to delete.
        :return: a message if the package repository is deleted or not.
        :rtype: str
        """

        response = self._session.delete(
            self._session.urljoin(self.RESOURCE_PATH, repo_id).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
            },
        )

        return response.json().get('message')


class PackageRepository(Base):
    pass
