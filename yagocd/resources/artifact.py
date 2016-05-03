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

import time

from yagocd.resources import BaseManager, Base


class ArtifactManager(BaseManager):
    """
    The artifacts API allows users to query and create artifacts of a job.
    """

    def __init__(
        self,
        session,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Constructs instance of ``ArtifactManager``.
        Parameters to the constructor and methods of the class could be duplicated. That is because of two use cases
        of this class:
            1. When the class being instantiated from :class:`yagocd.client.Client`, we don't know all the necessary
             parameters yet, but we need an instance to work with. So we skip parameters instantiation in constructor,
             but require them for each method.
            2. When the class being used from :class:`yagocd.resources.job.JobInstance` - in this case we already
            know all required parameters, so we can instantiate `ArtifactManager` with them.

        :param session: session object from client.
        :type session: yagocd.session.Session.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        """
        super(ArtifactManager, self).__init__(session)

        self.base_api = self._session.base_api(api_path='')

        self._pipeline_name = pipeline_name
        self._pipeline_counter = pipeline_counter
        self._stage_name = stage_name
        self._stage_counter = stage_counter
        self._job_name = job_name

    def list(
        self,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Lists all available artifacts in a job.

        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: An array of :class:`yagocd.resources.artifact.Artifact`.
        :rtype: list of yagocd.resources.artifact.Artifact
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.get(
            path=(
                '{base_api}'
                '/files'
                '/{pipeline_name}'
                '/{pipeline_counter}'
                '/{stage_name}'
                '/{stage_counter}'
                '/{job_name}.json'
            ).format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name
            ),
        )
        artifacts = list()
        for data in response.json():
            artifacts.append(Artifact(session=self._session, data=data))

        return artifacts

    def directory(
        self,
        path,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None,
    ):
        """
        Gets an artifact directory by its path.

        :note: The `path` can be a nested directory for e.g. target/dist.zip

        :warning: Since it may take an undetermined amount of time to compress
        a directory, the server may return a `202 Accepted` code to indicate that
        it is compressing the requested directory.
        Users are expected to poll the url every few seconds to check if the
        directory is available.

        :param path: path to directory.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return:
            * A status code `202 Accepted` to acknowledge your request to compress
              the contents of the requested directory.
            * The requested directory contents in the form of a zip file.
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.get(
            path=(
                '{base_api}'
                '/files'
                '/{pipeline_name}'
                '/{pipeline_counter}'
                '/{stage_name}'
                '/{stage_counter}'
                '/{job_name}'
                '/{path_to_folder}').format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name,
                path_to_folder=path
            ),
        )

        return response.content

    def directory_wait(
        self,
        path,
        timeout=60,
        backoff=0.4,
        max_wait=4,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None,
    ):
        """
        Gets an artifact directory by its path.
        This method wraps original `directory` method, adding
        timeout to wait  for directory to be available.

        :param path: path to directory.
        :param timeout: timeout in seconds to wait for directory.
        :param backoff: backoff value.
        :param max_wait: maximum wait amount.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: The requested directory contents in the form of a zip file.
        """
        start_time = time.time()
        time_elapsed = 0
        counter = 0
        directory_zip = None

        while time_elapsed < timeout:
            directory_zip = self.directory(path, pipeline_name, pipeline_counter, stage_name, stage_counter, job_name)
            if directory_zip:
                break

            time.sleep(min(backoff * (2 ** counter), max_wait))
            counter += 1
            time_elapsed = time.time() - start_time

        return directory_zip

    def create(
        self,
        path,
        filename,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None,
    ):
        """
        Uploads a local file as an artifact.

        :param path: path to the file within job directory.
        :param filename: the contents file to be uploaded.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: an acknowledgement that the file was created.
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.post(
            path=(
                '{base_api}'
                '/files'
                '/{pipeline_name}'
                '/{pipeline_counter}'
                '/{stage_name}'
                '/{stage_counter}'
                '/{job_name}'
                '/{path_to_file}'
            ).format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name,
                path_to_file=path
            ),
            files={'file': open(filename, 'rb')}
        )

        return response.text

    def append(
        self,
        path,
        filename,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None,
    ):
        """
        Appends a local file to an existing artifact.

        :param path: path to the file within job directory.
        :param filename: the contents file to be uploaded.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: an acknowledgement that the file was created.
        """
        assert self._pipeline_name or pipeline_name
        assert self._pipeline_counter or pipeline_counter
        assert self._stage_name or stage_name
        assert self._stage_counter or stage_counter
        assert self._job_name or job_name

        response = self._session.put(
            path=(
                '{base_api}'
                '/files'
                '/{pipeline_name}'
                '/{pipeline_counter}'
                '/{stage_name}'
                '/{stage_counter}'
                '/{job_name}'
                '/{path_to_file}'
            ).format(
                base_api=self.base_api,
                pipeline_name=self._pipeline_name or pipeline_name,
                pipeline_counter=self._pipeline_counter or pipeline_counter,
                stage_name=self._stage_name or stage_name,
                stage_counter=self._stage_counter or stage_counter,
                job_name=self._job_name or job_name,
                path_to_file=path
            ),
            files={'file': open(filename, 'rb')}
        )

        return response.text


class Artifact(Base):
    def files(self):
        return [ArtifactFile(session=self._session, data=data) for data in self.data.files]


class ArtifactFile(Base):
    def fetch(self):
        response = self._session.get(self.data.url)
        return response.text
