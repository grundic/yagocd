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

import copy
from yagocd.session import Session
from yagocd.resources.agent import AgentManager
from yagocd.resources.artifact import ArtifactManager
from yagocd.resources.configuration import ConfigurationManager
from yagocd.resources.feed import FeedManager
from yagocd.resources.job import JobManager
from yagocd.resources.material import MaterialManager
from yagocd.resources.pipeline import PipelineManager
from yagocd.resources.property import PropertyManager
from yagocd.resources.stage import StageManager
from yagocd.resources.user import UserManager


class Yagocd(object):
    """
    Main class of the package, that gives user access to Go REST API methods.
    """

    DEFAULT_OPTIONS = {
        'server': 'http://localhost:8153',
        'context_path': 'go/',
        'api_path': 'api/',
        'verify': True,
        'headers': {
            'Accept': 'application/vnd.go.cd.v1+json',
        }
    }

    def __init__(self, server=None, auth=None, options=None):
        """
        Construct a GOCD client instance.

        :param server: url of the Go server
        :param auth: authorization, that will be passed to requests.
        Could tuple of (username, password) for basic authentication.
        :param options: dictionary of additional options.
            * context_path -- server context path to use (default is ``go/``)
            * api_path -- api endpoint to use. By default ``api/`` will be used, but in some cases this will be
            overwritten by some managers, because of API.
            * verify -- verify SSL certs. Defaults to ``True``.
            * headers -- default headers for requests (default is ``'Accept': 'application/vnd.go.cd.v1+json'``)
        """
        options = {} if options is None else options

        if server is not None:
            options['server'] = server

        merged = copy.deepcopy(self.DEFAULT_OPTIONS)
        merged.update(options)

        self._session = Session(auth, merged)

    @property
    def server_url(self):
        """
        Property for getting server url.
        :return: server url for this instance.
        """
        return self._session.server_url

    @property
    def agents(self):
        """
        Property for accessing ``AgentManager`` instance, which is used to manage agents.

        :rtype: yagocd.resources.agent.AgentManager
        """
        return AgentManager(session=self._session)

    @property
    def artifacts(self):
        """
        Property for accessing ``ArtifactManager`` instance, which is used to manage artifacts.

        :rtype: yagocd.resources.artifact.ArtifactManager
        """
        return ArtifactManager(session=self._session)

    @property
    def configurations(self):
        """
        Property for accessing ``ConfigurationManager`` instance, which is used to manage configurations.

        :rtype: yagocd.resources.configuration.ConfigurationManager
        """
        return ConfigurationManager(session=self._session)

    @property
    def feeds(self):
        """
        Property for accessing ``FeedManager`` instance, which is used to manage feeds.

        :rtype: yagocd.resources.feed.FeedManager
        """
        return FeedManager(session=self._session)

    @property
    def jobs(self):
        """
        Property for accessing ``JobManager`` instance, which is used to manage feeds.

        :rtype: yagocd.resources.job.JobManager
        """
        return JobManager(session=self._session)

    @property
    def materials(self):
        """
        Property for accessing ``MaterialManager`` instance, which is used to manage materials.

        :rtype: yagocd.resources.material.MaterialManager
        """
        return MaterialManager(session=self._session)

    @property
    def pipelines(self):
        """
        Property for accessing ``PipelineManager`` instance, which is used to manage pipelines.

        :rtype: yagocd.resources.pipeline.PipelineManager
        """
        return PipelineManager(session=self._session)

    @property
    def properties(self):
        """
        Property for accessing ``PropertyManager`` instance, which is used to manage properties of the jobs.

        :rtype: yagocd.resources.property.PropertyManager
        """
        return PropertyManager(session=self._session)

    @property
    def stages(self):
        """
        Property for accessing ``StageManager`` instance, which is used to manage stages.

        :rtype: yagocd.resources.stage.StageManager
        """
        return StageManager(session=self._session)

    @property
    def users(self):
        """
        Property for accessing ``UserManager`` instance, which is used to manage users.

        :rtype: yagocd.resources.user.UserManager
        """
        return UserManager(session=self._session)
