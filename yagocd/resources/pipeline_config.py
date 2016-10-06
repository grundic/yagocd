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

from easydict import EasyDict

from yagocd.resources import BaseManager
from yagocd.util import since


@since('15.3.0')
class PipelineConfigManager(BaseManager):
    """
    The pipeline config API allows users with administrator role to manage pipeline config.

    `Official documentation. <https://api.go.cd/current/#pipeline-config>`_

    :versionadded: 15.3.0.
    """

    ACCEPT_HEADER = 'application/vnd.go.cd.v2+json'

    VERSION_TO_ACCEPT_HEADER = {
        '16.6.0': 'application/vnd.go.cd.v1+json',
    }

    def __init__(self, session, pipeline_name=None):
        super(PipelineConfigManager, self).__init__(session)
        self._pipeline_name = pipeline_name

    def __getitem__(self, pipeline_name):
        """
        Method add possibility to get pipeline config by the name using dictionary like syntax.

        :param pipeline_name: name of the pipeline.
        :return: tuple of pipeline config object and current ETag value.
        :rtype: (dict, str)
        """
        return self.get(pipeline_name=pipeline_name)

    def get(self, pipeline_name=None):
        """
        Gets pipeline config for specified pipeline name.

        :versionadded: 15.3.0.

        :param pipeline_name: name of the pipeline. Could be skipped
          if name was configured from constructor.
        :return: tuple of pipeline config object and current ETag value.
        :rtype: (dict, str)
        """
        assert self._pipeline_name or pipeline_name

        response = self._session.get(
            path='{base_api}/admin/pipelines/{pipeline_name}'.format(
                base_api=self.base_api, pipeline_name=self._pipeline_name or pipeline_name
            ),
            headers={'Accept': self._accept_header()},
        )

        etag = response.headers['ETag']
        return EasyDict(response.json()), etag

    def edit(self, config, etag, pipeline_name=None):
        """
        Update pipeline config for specified pipeline name.

        :versionadded: 15.3.0.

        :param config: dictionary containing new configuration
          for a given pipeline.
        :param etag: etag value from current configuration resource.
        :param pipeline_name: name of the pipeline. Could be skipped
          if name was configured from constructor.
        :return: tuple of updated pipeline config object and updated ETag.
        :rtype: (dict, str)
        """
        assert self._pipeline_name or pipeline_name
        response = self._session.put(
            path='{base_api}/admin/pipelines/{pipeline_name}'.format(
                base_api=self.base_api, pipeline_name=self._pipeline_name or pipeline_name
            ),
            data=json.dumps(config),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
                'If-Match': etag,
            },
        )

        etag = response.headers['ETag']
        return EasyDict(response.json()), etag

    def create(self, config):
        """
        Creates new pipeline.

        :versionadded: 15.3.0.

        :param config: configuration data.
        :return: tuple of created pipeline config object and ETag.
        :rtype: (dict, str)
        """
        response = self._session.post(
            path='{base_api}/admin/pipelines'.format(base_api=self.base_api),
            data=json.dumps(config),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
            },
        )

        etag = response.headers['ETag']
        return EasyDict(response.json()), etag

    @since('16.6.0')
    def delete(self, pipeline_name=None):
        """
        Deletes a pipeline.

        :versionadded: 16.6.0.

        :param pipeline_name: name of pipeline to delete
        :return: A message confirmation if the pipeline was deleted.
        :rtype: str
        """
        assert self._pipeline_name or pipeline_name

        response = self._session.delete(
            path='{base_api}/admin/pipelines/{pipeline_name}'.format(
                base_api=self.base_api, pipeline_name=self._pipeline_name or pipeline_name
            ),
            headers={
                'Accept': self._accept_header(),
            },
        )

        return response.json().get('message')
