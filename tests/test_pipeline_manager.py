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

from yagocd.client import Yagocd
from yagocd.session import Session
from yagocd.resources import pipeline

import mock
import pytest
from requests import HTTPError


class BaseTestPipelineManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return pipeline.PipelineManager(session=session)


class TestTieDescendants(BaseTestPipelineManager):
    def test_tie_descendants(self, session, manager):
        child = pipeline.PipelineEntity(
            session=session,
            data={'name': 'child1', 'materials': {}}
        )

        parent = pipeline.PipelineEntity(
            session=session,
            data={'name': 'parent1', 'materials': [{'description': 'child1', 'type': 'Pipeline'}]}
        )

        pipelines = [child, parent]

        manager.tie_descendants(pipelines)
        assert child.descendants == [parent]


class TestList(BaseTestPipelineManager):
    def test_list_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list") as cass:
            manager.list()
            assert cass.requests[0].path == '/go/api/config/pipeline_groups'

    def test_list_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list") as cass:
            manager.list()
            assert cass.requests[0].method == 'GET'

    def test_list_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list") as cass:
            manager.list()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_list_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list") as cass:
            manager.list()
            assert cass.responses[0]['status']['code'] == 200

    def test_list_is_not_empty(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            result = manager.list()
            assert len(result) > 0

    def test_elements_in_list_are_pipelines_entities(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            result = manager.list()
            assert all(isinstance(i, pipeline.PipelineEntity) for i in result)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.tie_descendants')
    def test_tie_descendants_is_called(self, mock_tie_descendants, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            manager.list()
            mock_tie_descendants.assert_called()


class TestFind(BaseTestPipelineManager):
    @mock.patch('yagocd.resources.pipeline.PipelineManager.list')
    def test_list_is_called(self, mock_list, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            name = 'Production_Services'
            manager.find(name)
            mock_list.assert_called()

    def test_find_non_existing(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            result = manager.find('This_Pipeline_Doesnt_Exists')
            assert result is None

    def test_find_returns_pipeline_entity(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            name = 'Production_Services'
            result = manager.find(name)
            assert isinstance(result, pipeline.PipelineEntity)

    def test_find_returns_entity_with_same_name(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            name = 'Production_Services'
            result = manager.find(name)
            assert result.data.name == name


class TestHistory(BaseTestPipelineManager):
    def test_history_non_existing(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_non_existing"):
            with pytest.raises(HTTPError):
                manager.history("pipeline_non_existing")

    def test_history_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.history(name)
            assert cass.requests[0].path == '/go/api/pipelines/{name}/history/{offset}'.format(
                name=name, offset=0
            )

    def test_history_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.history(name)
            assert cass.requests[0].method == 'GET'

    def test_history_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.history(name)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_history_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.history(name)
            assert cass.responses[0]['status']['code'] == 200

    def test_history(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website"):
            name = "Consumer_Website"
            result = manager.history(name)

            assert all(isinstance(i, pipeline.PipelineInstance) for i in result)
            assert all(i.data.name == name for i in result)


class TestGet(BaseTestPipelineManager):
    def test_get_non_existing(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_non_existing"):
            with pytest.raises(HTTPError):
                manager.get("pipeline_instance_non_existing", 1)

    def test_get_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_Consumer_Website") as cass:
            name = "Consumer_Website"
            counter = 2
            manager.get(name, counter)
            assert cass.requests[0].path == '/go/api/pipelines/{name}/instance/{counter}'.format(
                name=name, counter=counter
            )

    def test_get_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.get(name, 2)
            assert cass.requests[0].method == 'GET'

    def test_get_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.get(name, 2)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_get_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_Consumer_Website") as cass:
            name = "Consumer_Website"
            manager.get(name, 2)
            assert cass.responses[0]['status']['code'] == 200

    def test_get(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_Consumer_Website"):
            name = "Consumer_Website"
            result = manager.get(name, 2)

            assert isinstance(result, pipeline.PipelineInstance)
            assert result.data.name == name

    def test_status(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/status_Consumer_Website"):
            name = "Consumer_Website"
            result = manager.status(name)

            assert result == {'paused': False, 'schedulable': True, 'locked': False}


class TestPause(BaseTestPipelineManager):
    def test_pause(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website"):
            name = "Consumer_Website"
            reason = 'Test pause reason'
            manager.unpause(name)

            result = manager.pause(name, reason)

            assert result is None
            assert manager.status(name) == {'paused': True, 'schedulable': False, 'locked': False}

            manager.unpause(name)


class TestUnPause(BaseTestPipelineManager):
    def test_unpause(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website"):
            name = "Consumer_Website"
            manager.pause(name, '')

            result = manager.unpause(name)
            assert result is None

            assert manager.status(name) == {'paused': False, 'schedulable': True, 'locked': False}


class TestReleaseLock(BaseTestPipelineManager):
    #
    # def test_release_lock(self, manager, my_vcr):
    #     with my_vcr.use_cassette("pipeline/release_lock_Consumer_Website"):
    #         name = "Consumer_Website"
    #         manager.release_lock(name)
    #         # TODO: this fails, find a way to fix.
    #
    pass


class TestSchedule(BaseTestPipelineManager):
    # # TODO: implement when schedule would be implemented
    # def test_schedule(self, manager, my_vcr):
    #     with my_vcr.use_cassette("pipeline/schedule_<name_of_pipeline>'"):
    #         assert 0
    pass
