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

from yagocd.resources.base import Base


class ArtifactManager(object):
    def __init__(self, client):
        """
        :type client: yagocd.client.Client
        """
        self._client = client
        self.base_api = self._client.base_api(rest_base_path='files/')

    def list(self, pipeline_name, pipeline_counter, stage_name, stage_counter, job_name):
        response = self._client.get(
            path='{base_api}/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}.json'.format(
                base_api=self.base_api,
                pipeline_name=pipeline_name,
                pipeline_counter=pipeline_counter,
                stage_name=stage_name,
                stage_counter=stage_counter,
                job_name=job_name
            ),
        )
        artifacts = list()
        for data in response.json():
            artifacts.append(Artifact(client=self._client, data=data))

        return artifacts


class Artifact(Base):
    def files(self):
        return [ArtifactFile(client=self._client, data=data) for data in self.data.files]


class ArtifactFile(Base):
    def fetch(self):
        response = self._client.get(self.data.url)
        return response.text


if __name__ == '__main__':
    pass
