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

import pytest

from yagocd import Yagocd
from yagocd.resources import agent, artifact, configuration, feed, job, material, pipeline, property as prop, stage, user


class TestInit(object):
    def test_default(self):
        try:
            Yagocd()
        except Exception as e:
            assert False, "Unexpected exception raised: {0}".format(e)

    def test_set_server(self):
        go = Yagocd(server='http://example.com')
        assert go.server_url == 'http://example.com'

    def test_set_server_from_options(self):
        go = Yagocd(options=dict(server='http://example.com'))
        assert go.server_url == 'http://example.com'

    def test_set_verify(self):
        go = Yagocd(options=dict(verify=False))
        assert go._session._options['verify'] == False

    def test_set_headers(self):
        go = Yagocd(options=dict(headers=dict(Accept='foo/bar')))
        assert go._session._options['headers']['Accept'] == 'foo/bar'


class TestServerUrl(object):
    def test_default(self):
        assert Yagocd().server_url == 'http://localhost:8153'


class TestManagers(object):
    @pytest.fixture()
    def go_fixture(self):
        return Yagocd()

    def test_agents(self, go_fixture):
        assert isinstance(go_fixture.agents, agent.AgentManager)

    def test_artifacts(self, go_fixture):
        assert isinstance(go_fixture.artifacts, artifact.ArtifactManager)

    def test_configurations(self, go_fixture):
        assert isinstance(go_fixture.configurations, configuration.ConfigurationManager)

    def test_feeds(self, go_fixture):
        assert isinstance(go_fixture.feeds, feed.FeedManager)

    def test_jobs(self, go_fixture):
        assert isinstance(go_fixture.jobs, job.JobManager)

    def test_materials(self, go_fixture):
        assert isinstance(go_fixture.materials, material.MaterialManager)

    def test_pipelines(self, go_fixture):
        assert isinstance(go_fixture.pipelines, pipeline.PipelineManager)

    def test_properties(self, go_fixture):
        assert isinstance(go_fixture.properties, prop.PropertyManager)

    def test_stages(self, go_fixture):
        assert isinstance(go_fixture.stages, stage.StageManager)

    def test_users(self, go_fixture):
        assert isinstance(go_fixture.users, user.UserManager)
