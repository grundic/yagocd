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
    def __init__(self, session, pipeline_name, pipeline_counter, stage_name, stage_counter, job_name):
        """
        :type session: yagocd.session.Session
        """
        self._session = session
        self.base_api = self._session.base_api(api_path='')

        self._pipeline_name = pipeline_name
        self._pipeline_counter = pipeline_counter
        self._stage_name = stage_name
        self._stage_counter = stage_counter
        self._job_name = job_name

    def list(self):
        response = self._session.get(
            path='{base_api}/files/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}.json'.format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name,
                pipeline_counter=self._pipeline_counter,
                stage_name=self._stage_name,
                stage_counter=self._stage_counter,
                job_name=self._job_name
            ),
        )
        artifacts = list()
        for data in response.json():
            artifacts.append(Artifact(session=self._session, data=data))

        return artifacts

    def directory(self, path):
        raise NotImplementedError

    def create(self, path, filename):
        raise NotImplementedError


class Artifact(Base):
    def files(self):
        return [ArtifactFile(session=self._session, data=data) for data in self.data.files]


class ArtifactFile(Base):
    def fetch(self):
        response = self._session.get(self.data.url)
        return response.text


if __name__ == '__main__':
    pass
