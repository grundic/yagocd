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
import hashlib

from yagocd.resources import pipeline

import mock
import pytest
from requests import HTTPError


class BaseTestPipelineManager(object):
    @staticmethod
    def get_suffix(*args):
        m = hashlib.md5()
        m.update('|'.join([str(x) for x in args]).encode('utf-8'))
        m.hexdigest()
        return m.hexdigest()[:8]

    @pytest.fixture()
    def manager(self, session_fixture):
        return pipeline.PipelineManager(session=session_fixture)


class TestTieDescendants(BaseTestPipelineManager):
    def test_tie_descendants(self, session_fixture, manager):
        child = pipeline.PipelineEntity(
            session=session_fixture,
            data={'name': 'child1', 'materials': {}}
        )

        parent = pipeline.PipelineEntity(
            session=session_fixture,
            data={'name': 'parent1', 'materials': [{'description': 'child1', 'type': 'Pipeline'}]}
        )

        pipelines = [child, parent]

        manager.tie_pipelines(pipelines)
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

    @mock.patch('yagocd.resources.pipeline.PipelineManager.tie_pipelines')
    def test_tie_descendants_is_called(self, mock_tie_pipelines, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list"):
            manager.list()
            mock_tie_pipelines.assert_called()


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


class TestFullHistory(BaseTestPipelineManager):
    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_is_called(self, history_mock, manager, my_vcr):
        history_mock.side_effect = [['foo', 'bar', 'baz'], []]

        name = "Consumer_Website"
        list(manager.full_history(name))

        calls = [mock.call(name, 0), mock.call(name, 3)]
        history_mock.assert_has_calls(calls)


class TestLast(BaseTestPipelineManager):
    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_is_called(self, history_mock, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website"):
            name = "Consumer_Website"
            manager.last(name)
            history_mock.assert_called_with(name=name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_last_return_last(self, history_mock, manager, my_vcr):
        history_mock.return_value = ['foo', 'bar', 'baz']
        with my_vcr.use_cassette("pipeline/history_Consumer_Website"):
            name = "Consumer_Website"
            assert manager.last(name) == 'foo'


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

            expected_items = {'paused': False, 'schedulable': True, 'locked': False}
            for name, value in expected_items.items():
                assert result[name] == value


class TestPause(BaseTestPipelineManager):
    NAME = 'Consumer_Website'
    REASON = 'Test pause reason'

    def test_pause_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website") as cass:
            manager.pause(self.NAME, self.REASON)
            assert cass.requests[0].path == '/go/api/pipelines/{name}/pause'.format(name=self.NAME)

    def test_pause_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website") as cass:
            manager.pause(self.NAME, self.REASON)
            assert cass.requests[0].method == 'POST'

    def test_pause_request_accept_header(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website") as cass:
            manager.pause(self.NAME, self.REASON)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_pause_request_confirm_header(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website") as cass:
            manager.pause(self.NAME, self.REASON)
            assert cass.requests[0].headers['Confirm'] == 'true'

    def test_pause_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website") as cass:
            manager.pause(self.NAME, self.REASON)
            assert cass.responses[0]['status']['code'] == 200

    def test_pause(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_Consumer_Website_complex"):
            manager.unpause(self.NAME)

            result = manager.pause(self.NAME, self.REASON)

            assert result is None
            expected_items = {'paused': True, 'schedulable': False, 'locked': False}
            status = manager.status(self.NAME)
            for item_name, value in expected_items.items():
                assert status[item_name] == value

            manager.unpause(self.NAME)


class TestUnPause(BaseTestPipelineManager):
    NAME = "Consumer_Website"

    def test_unpause_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website") as cass:
            manager.unpause(self.NAME)
            assert cass.requests[0].path == '/go/api/pipelines/{name}/unpause'.format(name=self.NAME)

    def test_unpause_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website") as cass:
            manager.unpause(self.NAME)
            assert cass.requests[0].method == 'POST'

    def test_unpause_request_accept_header(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website") as cass:
            manager.unpause(self.NAME)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_unpause_request_confirm_header(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website") as cass:
            manager.unpause(self.NAME)
            assert cass.requests[0].headers['Confirm'] == 'true'

    def test_unpause_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website") as cass:
            manager.unpause(self.NAME)
            assert cass.responses[0]['status']['code'] == 200

    def test_unpause(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_Consumer_Website_complex"):
            manager.pause(self.NAME, '')

            result = manager.unpause(self.NAME)
            assert result is None

            expected_items = {'paused': False, 'schedulable': True, 'locked': False}
            status = manager.status(self.NAME)
            for name, value in expected_items.items():
                assert status[name] == value


class TestReleaseLock(BaseTestPipelineManager):
    def test_release_lock_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock") as cass:
            name = "Deploy_UAT"
            manager.release_lock(name)
            assert cass.requests[0].path == '/go/api/pipelines/{name}/releaseLock'.format(
                name=name
            )

    def test_release_lock_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock") as cass:
            name = "Deploy_UAT"
            manager.release_lock(name)
            assert cass.requests[0].method == 'POST'

    def test_release_lock_request_accept_header(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock") as cass:
            name = "Deploy_UAT"
            manager.release_lock(name)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_release_lock_request_confirm_header(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock") as cass:
            name = "Deploy_UAT"
            manager.release_lock(name)
            assert cass.requests[0].headers['Confirm'] == 'true'

    def test_release_lock_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock") as cass:
            name = "Deploy_UAT"
            manager.release_lock(name)
            assert cass.responses[0]['status']['code'] == 200

    def test_release_lock_return_value(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock"):
            name = "Deploy_UAT"
            result = manager.release_lock(name)
            assert result == 'pipeline lock released for {0}\n'.format(name)


class TestSchedule(BaseTestPipelineManager):
    NAME = "TestSchedule"

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_schedule_request_url(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        with my_vcr.use_cassette("pipeline/schedule-{0}".format(suffix)) as cass:
            manager.schedule(
                name='{0}-{1}'.format(self.NAME, suffix),
                variables=variables,
                secure_variables=secure_variables
            )
            assert cass.requests[0].path == '/go/api/pipelines/{name}/schedule'.format(
                name='{0}-{1}'.format(self.NAME, suffix)
            )

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_schedule_request_method(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        with my_vcr.use_cassette("pipeline/schedule-{0}".format(suffix)) as cass:
            manager.schedule(
                name='{0}-{1}'.format(self.NAME, suffix),
                variables=variables,
                secure_variables=secure_variables
            )
            assert cass.requests[0].method == 'POST'

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_schedule_request_headers(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        with my_vcr.use_cassette("pipeline/schedule-{0}".format(suffix)) as cass:
            manager.schedule(
                name='{0}-{1}'.format(self.NAME, suffix),
                variables=variables,
                secure_variables=secure_variables
            )
            assert cass.requests[0].headers['accept'] == 'application/json'
            assert cass.requests[0].headers['content-type'] == 'application/json'
            assert cass.requests[0].headers['Confirm'] == 'true'

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_schedule_response_code(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        with my_vcr.use_cassette("pipeline/schedule-{0}".format(suffix)) as cass:
            manager.schedule(
                name='{0}-{1}'.format(self.NAME, suffix),
                variables=variables,
                secure_variables=secure_variables
            )
            assert cass.responses[0]['status']['code'] == 202

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_schedule_return_value(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        with my_vcr.use_cassette("pipeline/schedule-{0}".format(suffix)):
            result = manager.schedule(
                name='{0}-{1}'.format(self.NAME, suffix),
                variables=variables,
                secure_variables=secure_variables
            )
            assert result == 'Request to schedule pipeline {0}-{1} accepted\n'.format(self.NAME, suffix)


class TestScheduleWithInstance(BaseTestPipelineManager):
    NAME = "TestScheduleWithInstance"

    def _do_schedule_with_instance(self, my_vcr, cass_name, manager, pipeline_name, variables, secure_variables):
        should_wait = False
        with my_vcr.use_cassette(cass_name) as cass:
            if not len(cass.requests):
                should_wait = True

        if should_wait:
            pipeline_instance = manager.last(pipeline_name)
            while pipeline_instance and not pipeline_instance.data.can_run:
                print("Sleeping...")
                time.sleep(10)
                pipeline_instance = manager.last(pipeline_name)

            backoff = 4
            max_tries = 50
        else:
            backoff = 0
            max_tries = 20

        with my_vcr.use_cassette(cass_name):
            return manager.schedule_with_instance(
                name=pipeline_name,
                variables=variables,
                secure_variables=secure_variables,
                backoff=backoff,
                max_tries=max_tries
            )

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    @mock.patch('yagocd.resources.pipeline.PipelineManager.schedule')
    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_schedule_is_called(self, history_mock, schedule_mock, session_fixture, manager, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        history_mock.return_value = [pipeline.PipelineInstance(session_fixture, dict(counter=1))]
        manager.schedule_with_instance(
            name='{0}-{1}'.format(self.NAME, suffix),
            variables=variables,
            secure_variables=secure_variables,
            backoff=0
        )
        schedule_mock.assert_called()

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_return_value(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        result = self._do_schedule_with_instance(
            my_vcr,
            "pipeline/schedule_with_instance-{0}".format(suffix),
            manager,
            '{0}-{1}'.format(self.NAME, suffix),
            variables,
            secure_variables
        )
        assert isinstance(result, pipeline.PipelineInstance)

    @pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
    @pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
    def test_empty_history(self, manager, my_vcr, variables, secure_variables):
        suffix = self.get_suffix(variables, secure_variables)
        result = self._do_schedule_with_instance(
            my_vcr,
            "pipeline/schedule_with_instance_custom_history-{0}".format(suffix),
            manager,
            '{0}-{1}'.format(self.NAME, suffix),
            variables,
            secure_variables
        )
        assert isinstance(result, pipeline.PipelineInstance)
