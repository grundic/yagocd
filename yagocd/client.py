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

from yagocd.resources import BaseManager
from yagocd.resources.agent import AgentManager
from yagocd.resources.artifact import ArtifactManager
from yagocd.resources.configuration import ConfigurationManager
from yagocd.resources.elastic_profile import ElasticAgentProfileManager
from yagocd.resources.encryption import EncryptionManager
from yagocd.resources.environment import EnvironmentManager
from yagocd.resources.feed import FeedManager
from yagocd.resources.job import JobManager
from yagocd.resources.material import MaterialManager
from yagocd.resources.notification_filter import NotificationFilterManager
from yagocd.resources.package import PackageManager
from yagocd.resources.package_repository import PackageRepositoryManager
from yagocd.resources.pipeline import PipelineManager
from yagocd.resources.pipeline_config import PipelineConfigManager
from yagocd.resources.plugin_info import PluginInfoManager
from yagocd.resources.property import PropertyManager
from yagocd.resources.scm import SCMManager
from yagocd.resources.stage import StageManager
from yagocd.resources.template import TemplateManager
from yagocd.resources.user import UserManager
from yagocd.resources.version import VersionManager
from yagocd.session import Session


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
            'Accept': BaseManager.ACCEPT_HEADER,
        }
    }

    def __init__(self, server=None, auth=None, options=None):
        """
        Construct a GoCD client instance.

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

        # manager instances
        self._agent_manager = None
        self._artifact_manager = None
        self._configuration_manager = None
        self._elastic_agent_profile_manager = None
        self._encryption_manager = None
        self._environment_manager = None
        self._feed_manager = None
        self._job_manager = None
        self._material_manager = None
        self._notification_filter_manager = None
        self._package_manager = None
        self._package_repository_manager = None
        self._pipeline_manager = None
        self._pipeline_config_manager = None
        self._plugin_info_manager = None
        self._property_manager = None
        self._scm_manager = None
        self._stage_manager = None
        self._template_manager = None
        self._user_manager = None
        self._version_manager = None

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
        Property for accessing :class:`AgentManager` instance, which is used to manage agents.

        :rtype: yagocd.resources.agent.AgentManager
        """
        if self._agent_manager is None:
            self._agent_manager = AgentManager(session=self._session)
        return self._agent_manager

    @property
    def artifacts(self):
        """
        Property for accessing :class:`ArtifactManager` instance, which is used to manage artifacts.

        :rtype: yagocd.resources.artifact.ArtifactManager
        """
        if self._artifact_manager is None:
            self._artifact_manager = ArtifactManager(session=self._session)
        return self._artifact_manager

    @property
    def configurations(self):
        """
        Property for accessing :class:`ConfigurationManager` instance, which is used to manage configurations.

        :rtype: yagocd.resources.configuration.ConfigurationManager
        """
        if self._configuration_manager is None:
            self._configuration_manager = ConfigurationManager(session=self._session)
        return self._configuration_manager

    @property
    def encryption(self):
        """
        Property for accessing :class:`EncryptionManager` instance,
        which is used to manage encryption.

        :rtype: yagocd.resources.encryption.EncryptionManager
        """
        if self._encryption_manager is None:
            self._encryption_manager = EncryptionManager(session=self._session)
        return self._encryption_manager

    @property
    def elastic_profiles(self):
        """
        Property for accessing :class:`ElasticAgentProfileManager` instance,
        which is used to manage elastic agent profiles.

        :rtype: yagocd.resources.elastic_profile.ElasticAgentProfileManager
        """
        if self._elastic_agent_profile_manager is None:
            self._elastic_agent_profile_manager = ElasticAgentProfileManager(session=self._session)
        return self._elastic_agent_profile_manager

    @property
    def environments(self):
        """
        Property for accessing :class:`EnvironmentManager` instance, which is used to manage environments.

        :rtype: yagocd.resources.environment.EnvironmentManager
        """
        if self._environment_manager is None:
            self._environment_manager = EnvironmentManager(session=self._session)
        return self._environment_manager

    @property
    def feeds(self):
        """
        Property for accessing :class:`FeedManager` instance, which is used to manage feeds.

        :rtype: yagocd.resources.feed.FeedManager
        """
        if self._feed_manager is None:
            self._feed_manager = FeedManager(session=self._session)
        return self._feed_manager

    @property
    def jobs(self):
        """
        Property for accessing :class:`JobManager` instance, which is used to manage feeds.

        :rtype: yagocd.resources.job.JobManager
        """
        if self._job_manager is None:
            self._job_manager = JobManager(session=self._session)
        return self._job_manager

    @property
    def notification_filters(self):
        """
        Property for accessing :class:`NotificationFilterManager` instance, which is used to manage notification
        filters.

        :rtype: yagocd.resources.notification_filter.NotificationFilterManager
        """
        if self._notification_filter_manager is None:
            self._notification_filter_manager = NotificationFilterManager(session=self._session)
        return self._notification_filter_manager

    @property
    def materials(self):
        """
        Property for accessing :class:`MaterialManager` instance, which is used to manage materials.

        :rtype: yagocd.resources.material.MaterialManager
        """
        if self._material_manager is None:
            self._material_manager = MaterialManager(session=self._session)
        return self._material_manager

    @property
    def packages(self):
        """
        Property for accessing :class:`PackageManager` instance, which is used to manage packages.

        :rtype: yagocd.resources.package.PackageManager
        """
        if self._package_manager is None:
            self._package_manager = PackageManager(session=self._session)
        return self._package_manager

    @property
    def package_repositories(self):
        """
        Property for accessing :class:`PackageRepositoryManager` instance, which is used to manage package repos.

        :rtype: yagocd.resources.package_repository.PackageRepositoryManager
        """
        if self._package_repository_manager is None:
            self._package_repository_manager = PackageRepositoryManager(session=self._session)
        return self._package_repository_manager

    @property
    def pipelines(self):
        """
        Property for accessing :class:`PipelineManager` instance, which is used to manage pipelines.

        :rtype: yagocd.resources.pipeline.PipelineManager
        """
        if self._pipeline_manager is None:
            self._pipeline_manager = PipelineManager(session=self._session)
        return self._pipeline_manager

    @property
    def pipeline_configs(self):
        """
        Property for accessing :class:`PipelineConfigManager` instance, which is used to manage pipeline configurations.

        :rtype: yagocd.resources.pipeline_config.PipelineConfigManager
        """
        if self._pipeline_config_manager is None:
            self._pipeline_config_manager = PipelineConfigManager(session=self._session)
        return self._pipeline_config_manager

    @property
    def plugin_info(self):
        """
        Property for accessing :class:`PluginInfoManager` instance, which is used to manage pipeline configurations.

        :rtype: yagocd.resources.plugin_info.PluginInfoManager
        """
        if self._plugin_info_manager is None:
            self._plugin_info_manager = PluginInfoManager(session=self._session)
        return self._plugin_info_manager

    @property
    def properties(self):
        """
        Property for accessing :class:`PropertyManager` instance, which is used to manage properties of the jobs.

        :rtype: yagocd.resources.property.PropertyManager
        """
        if self._property_manager is None:
            self._property_manager = PropertyManager(session=self._session)
        return self._property_manager

    @property
    def scms(self):
        """
        Property for accessing :class:`SCMManager` instance, which is used to manage pluggable SCM materials.

        :rtype: yagocd.resources.scm.SCMManager
        """
        if self._scm_manager is None:
            self._scm_manager = SCMManager(session=self._session)
        return self._scm_manager

    @property
    def stages(self):
        """
        Property for accessing :class:`StageManager` instance, which is used to manage stages.

        :rtype: yagocd.resources.stage.StageManager
        """
        if self._stage_manager is None:
            self._stage_manager = StageManager(session=self._session)
        return self._stage_manager

    @property
    def templates(self):
        """
        Property for accessing :class:`TemplateManager` instance, which is used to manage templates.

        :rtype: yagocd.resources.template.TemplateManager
        """
        if self._template_manager is None:
            self._template_manager = TemplateManager(session=self._session)
        return self._template_manager

    @property
    def users(self):
        """
        Property for accessing :class:`UserManager` instance, which is used to manage users.

        :rtype: yagocd.resources.user.UserManager
        """
        if self._user_manager is None:
            self._user_manager = UserManager(session=self._session)
        return self._user_manager

    @property
    def versions(self):
        """
        Property for accessing :class:`VersionManager` instance, which is used to get server info.

        :rtype: yagocd.resources.version.VersionManager
        """
        if self._version_manager is None:
            self._version_manager = VersionManager(session=self._session)
        return self._version_manager
