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

from yagocd.exception import YagocdException
from yagocd.resources import Base, BaseManager
from yagocd.util import RequireParamMixin, since


@since('14.3.0')
class ArtifactManager(BaseManager, RequireParamMixin):
    """
    The artifacts API allows users to query and create artifacts of a job.

    `Official documentation. <https://api.go.cd/current/#artifacts>`_

    :versionadded: 14.3.0.
    """

    RESOURCE_PATH = '{base_api}/files/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}/{job_name}'
    PATH_PARAMETERS = ['pipeline_name', 'pipeline_counter', 'stage_name', 'stage_counter', 'job_name']

    FOLDER_TYPE = 'folder'
    FILE_TYPE = 'file'

    TYPE_FIELD = 'type'
    NAME_FIELD = 'name'
    FILES_FIELD = 'files'

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

    def __iter__(self):
        """
        Method for iterating over all artifacts, using `walk`.

        :rtype: collections.Iterator[
            (str, list[yagocd.resources.artifact.Artifact], list[yagocd.resources.artifact.Artifact])
        ]
        """
        return iter(self.walk())

    def __getitem__(self, path):
        """
        Method for downloading artifact or directory zip by given path.

        :param path: path to the file or directory zip
        :return: the contents of the file you requested or
        directory contents in the form of a zip file.
        """
        return self.directory_wait(path=path)

    def list(  # noqa
        self,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):  # noqa
        """
        Lists all available artifacts in a job.

        :versionadded: 14.3.0.

        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: An array of :class:`yagocd.resources.artifact.Artifact`.
        :rtype: list of yagocd.resources.artifact.Artifact
        """

        func_args = locals()
        parameters = {p: self._require_param(p, func_args) for p in self.PATH_PARAMETERS}

        response = self._session.get(
            path=(self.RESOURCE_PATH + '.json').format(base_api=self.base_api, **parameters)
        )
        artifacts = list()
        for data in response.json():
            artifacts.append(Artifact(session=self._session, data=data))

        return artifacts

    def walk(
        self,
        top='/',
        topdown=True,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None
    ):
        """
        Artifact tree generator - analogue of `os.walk`.

        :param top: root path, from which traversal would be started.
        :param topdown: if is True or not specified, directories are scanned
        from top-down. If topdown is set to False, directories are scanned
        from bottom-up.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :rtype: collections.Iterator[
            (str, list[yagocd.resources.artifact.Artifact], list[yagocd.resources.artifact.Artifact])
        ]
        """
        artifacts = self.list(
            pipeline_name=pipeline_name,
            pipeline_counter=pipeline_counter,
            stage_name=stage_name,
            stage_counter=stage_counter,
            job_name=job_name
        )
        return self._json_walk(top=top, topdown=topdown, artifacts=artifacts)

    def _json_walk(self, top, topdown, artifacts):
        """
        JSON walker - analogue of `os.walk`.
        Recursively walks through internal representation of the Artifact object.

        :param top: top or root path from which to start traversing.
        :param topdown: if is True or not specified, directories are scanned
        from top-down. If topdown is set to False, directories are scanned
        from bottom-up.
        :param artifacts: original list of artifacts, obtained from `list` method.
        :rtype: collections.Iterator[
            (str, list[yagocd.resources.artifact.Artifact], list[yagocd.resources.artifact.Artifact])
        ]
        """
        folders = list()
        files = list()
        children = self._get_children(artifacts, top)
        if children is None:
            return

        for artifact in children:
            artifact_type = artifact.data.get(self.TYPE_FIELD)
            if artifact_type == self.FOLDER_TYPE:
                folders.append(artifact)
            elif artifact_type == self.FILE_TYPE:
                files.append(artifact)
            else:
                raise ValueError("Unknown artifact type '{}'!".format(artifact_type))

        if topdown:
            yield top, folders, files
        for folder in folders:
            new_path = self._session.urljoin(top, folder.data.get(self.NAME_FIELD))

            for x in self._json_walk(new_path, topdown, children):
                yield x

        if not topdown:
            yield top, folders, files

    def _get_children(self, artifacts, path):
        """
        Method for extracting artifact children from a given artifacts list by some path.

        :param artifacts: list of artifacts from which to extract path.
        :param path: string representing POSIX path.
        :return: nested artifacts, located at the given path.
        :rtype: list[yagocd.resources.artifact.Artifact]
        """
        if not path or path in ['/']:
            return artifacts

        for candidate in artifacts:
            if candidate.path.rstrip('/') == path.rstrip('/'):
                children = candidate.data.get(self.FILES_FIELD)
                if children is None:
                    return  # case for a file type
                else:
                    return [Artifact(session=self._session, data=data) for data in children]
        else:
            raise ValueError("Can't find requested path '{path}' in the given artifacts '{artifacts}'!".format(
                path=path, artifacts=artifacts)
            )

    def file(
        self,
        path,
        pipeline_name=None,
        pipeline_counter=None,
        stage_name=None,
        stage_counter=None,
        job_name=None,
    ):  # noqa
        """
        Gets an artifact file by its path.

        :versionadded: 14.3.0.

        :note: The `path_to_file` can be a nested file for e.g. `dist/foobar-widgets-1.2.0.jar`.

        :param path: path to the file.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: the contents of the file you requested.
        """
        return self.directory(
            path=path,
            pipeline_name=pipeline_name,
            pipeline_counter=pipeline_counter,
            stage_name=stage_name,
            stage_counter=stage_counter,
            job_name=job_name
        )

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

        :versionadded: 14.3.0.

        :note: The `path` can be a nested directory for e.g. target/dist.zip

        :warning: Since it may take an undetermined amount of time to compress \
        a directory, the server may return a `202 Accepted` code to indicate that \
        it is compressing the requested directory. \
        Users are expected to poll the url every few seconds to check if the \
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

        func_args = locals()
        parameters = {p: self._require_param(p, func_args) for p in self.PATH_PARAMETERS}

        response = self._session.get(
            path=self._session.urljoin(self.RESOURCE_PATH, path).format(base_api=self.base_api, **parameters)
        )

        if response.status_code == 202:
            return None

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

        :versionadded: 14.3.0.

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
            if directory_zip is not None:
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

        :versionadded: 14.3.0.

        :param path: path to the file within job directory.
        :param filename: the contents file to be uploaded.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: an acknowledgement that the file was created.
        """

        func_args = locals()
        parameters = {p: self._require_param(p, func_args) for p in self.PATH_PARAMETERS}

        response = self._session.post(
            path=self._session.urljoin(self.RESOURCE_PATH, path).format(base_api=self.base_api, **parameters),
            files={'file': open(filename, 'rb')},
            headers={
                'Confirm': 'true'
            },
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

        :versionadded: 14.3.0.

        :param path: path to the file within job directory.
        :param filename: the contents file to be uploaded.
        :param pipeline_name: name of the pipeline.
        :param pipeline_counter: pipeline counter.
        :param stage_name: name of the stage.
        :param stage_counter: stage counter.
        :param job_name: name of the job.
        :return: an acknowledgement that the file was created.
        """

        func_args = locals()
        parameters = {p: self._require_param(p, func_args) for p in self.PATH_PARAMETERS}

        response = self._session.put(
            path=self._session.urljoin(self.RESOURCE_PATH, path).format(base_api=self.base_api, **parameters),
            files={'file': open(filename, 'rb')}
        )

        return response.text


class Artifact(Base):
    """
    Class, representing artifact of the build.

    It could be one of file or folder.
    """

    SEP = '/'

    PART_COUNT = 5

    def __init__(self, session, data):
        super(Artifact, self).__init__(session, data)

        base = self._session.urljoin(self._session.server_url, self._session._options['context_path'], 'files')
        parts = self.data.url.replace(base, '').strip(self.SEP).split(self.SEP, self.PART_COUNT)

        self._pipeline_name = parts[0]
        self._pipeline_counter = parts[1]
        self._stage_name = parts[2]
        self._stage_counter = parts[3]
        self._job_name = parts[4]

        self._path = self.SEP + parts[5]
        if self.data.type == ArtifactManager.FOLDER_TYPE and not self._path.endswith(self.SEP):
            self._path += self.SEP

        self._manager = ArtifactManager(
            session=session,
            pipeline_name=self._pipeline_name,
            pipeline_counter=self._pipeline_counter,
            stage_name=self._stage_name,
            stage_counter=self._stage_counter,
            job_name=self._job_name
        )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        result = "<{cls}: '{path}'>".format(cls=self.__class__.__name__, path=self._path)
        return result

    def __iter__(self):
        return iter(self.walk())

    @property
    def pipeline_name(self):
        return self._pipeline_name

    @property
    def pipeline_counter(self):
        return self._pipeline_counter

    @property
    def stage_name(self):
        return self._stage_name

    @property
    def stage_counter(self):
        return self._stage_counter

    @property
    def job_name(self):
        return self._job_name

    @property
    def path(self):
        return self._path

    def walk(self, topdown=True):
        """
        Artifact tree generator - analogue of `os.walk`.

        :param topdown: if is True or not specified, directories are scanned
        from top-down. If topdown is set to False, directories are scanned
        from bottom-up.
        :rtype: collections.Iterator[
            (str, list[yagocd.resources.artifact.Artifact], list[yagocd.resources.artifact.Artifact])
        ]
        """
        return self._manager.walk(top=self._path, topdown=topdown)

    def fetch(self):
        """
        Method for getting artifact's content.
        Could only be applicable for file type.

        :return: content of the artifact.
        """
        if self.data.type == self._manager.FOLDER_TYPE:
            raise YagocdException("Can't fetch folder <{}>, only file!".format(self._path))

        response = self._session.get(self.data.url)
        return response.content
