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
import hashlib
import time

import mock
import pytest
from six import string_types

from tests import AbstractTestManager, ConfirmHeaderMixin, RequestContentTypeHeadersMixin, ReturnValueMixin
from yagocd.exception import RequestError
from yagocd.resources import material
from yagocd.resources import pipeline
from yagocd.resources import stage


@pytest.fixture()
def manager(session_fixture):
    return pipeline.PipelineManager(session=session_fixture)


class BaseTestPipelineManager(object):
    @staticmethod
    def get_suffix(*args):
        m = hashlib.md5()
        m.update('|'.join([str(x) for x in args]).encode('utf-8'))
        m.hexdigest()
        return m.hexdigest()[:8]

    @pytest.fixture()
    def mock_manager(self, mock_session):
        return pipeline.PipelineManager(session=mock_session)


class TestList(BaseTestPipelineManager, AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pipeline_list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/config/pipeline_groups'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert len(result) > 0
            assert all(isinstance(i, pipeline.PipelineEntity) for i in result)

        return check_value

    @mock.patch('yagocd.util.YagocdUtil.build_graph')
    def test_build_graph_is_called(self, mock_build_graph, manager, my_vcr):
        self._execute_test_action(manager, my_vcr)
        mock_build_graph.assert_called()


class TestFind(TestList):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, name=''):
        with my_vcr.use_cassette("pipeline/pipeline_list") as cass:
            return cass, manager.find(name)

    @pytest.fixture()
    def expected_return_type(self):
        return None

    @pytest.fixture()
    def expected_return_value(self):
        return None

    @mock.patch('yagocd.resources.pipeline.PipelineManager.list')
    def test_list_is_called(self, mock_list, manager):
        manager.find(mock.MagicMock())
        mock_list.assert_called()

    def test_find_non_existing(self, manager, my_vcr):
        name = 'This_Pipeline_Doesnt_Exists'
        cass, result = self._execute_test_action(manager, my_vcr, name)
        assert result is None

    def test_find_returns_pipeline_entity(self, manager, my_vcr):
        name = 'Production_Services'
        cass, result = self._execute_test_action(manager, my_vcr, name)
        assert isinstance(result, pipeline.PipelineEntity)

    def test_find_returns_entity_with_same_name(self, manager, my_vcr):
        name = 'Production_Services'
        cass, result = self._execute_test_action(manager, my_vcr, name)
        assert result.data.name == name


class TestHistory(BaseTestPipelineManager, AbstractTestManager, ReturnValueMixin):
    NAME = 'Consumer_Website'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_Consumer_Website") as cass:
            return cass, manager.history(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{name}/history/{offset}'.format(name=self.NAME, offset=0)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert len(result) > 0
            assert all(isinstance(i, pipeline.PipelineInstance) for i in result)
            assert all(i.data.name == self.NAME for i in result)

        return check_value

    def test_non_existing_history_raises_http_error(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/history_non_existing") as cass:
            with pytest.raises(RequestError):
                return cass, manager.history("pipeline_non_existing")


class TestFullHistory(BaseTestPipelineManager):
    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_is_called(self, history_mock, mock_manager):
        history_mock.side_effect = [['foo', 'bar', 'baz'], []]

        name = "Consumer_Website"
        list(mock_manager.full_history(name))

        calls = [mock.call(name, 0), mock.call(name, 3)]
        history_mock.assert_has_calls(calls)


class TestLast(BaseTestPipelineManager):
    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_history_is_called(self, history_mock, mock_manager):
        name = "Consumer_Website"
        mock_manager.last(name)
        history_mock.assert_called_with(name=name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.history')
    def test_last_return_last(self, history_mock, mock_manager):
        history_mock.return_value = ['foo', 'bar', 'baz']
        assert mock_manager.last(mock.MagicMock()) == 'foo'


class TestGet(BaseTestPipelineManager, AbstractTestManager, ReturnValueMixin):
    NAME = "Consumer_Website"
    COUNTER = 2

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_Consumer_Website") as cass:
            return cass, manager.get(self.NAME, self.COUNTER)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{name}/instance/{counter}'.format(
            name=self.NAME, counter=self.COUNTER
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return pipeline.PipelineInstance

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert result.data.name == self.NAME

        return check_value

    def test_get_non_existing(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/get_non_existing"):
            with pytest.raises(RequestError):
                manager.get("pipeline_instance_non_existing", 1)


class TestStatus(BaseTestPipelineManager, AbstractTestManager, ReturnValueMixin):
    NAME = "UnPausedPipeline"

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/status_{}".format(self.NAME)) as cass:
            return cass, manager.status(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{name}/status'.format(name=self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return dict

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            expected_items = {'paused': False, 'schedulable': True, 'locked': False}
            for name, value in expected_items.items():
                assert result[name] == value

        return check_value


class TestPause(BaseTestPipelineManager, AbstractTestManager, ConfirmHeaderMixin):
    NAME = 'UnPausedPipeline'
    REASON = 'Test pause reason'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_{}".format(self.NAME)) as cass:
            return cass, manager.pause(self.NAME, self.REASON)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{name}/pause'.format(name=self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    def test_pause(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/pause_{}_complex".format(self.NAME)):
            manager.unpause(self.NAME)

            result = manager.pause(self.NAME, self.REASON)

            assert result is None
            expected_items = {'paused': True, 'schedulable': False, 'locked': False}
            status = manager.status(self.NAME)
            for item_name, value in expected_items.items():
                assert status[item_name] == value

            manager.unpause(self.NAME)


class TestUnpause(BaseTestPipelineManager, AbstractTestManager, ConfirmHeaderMixin):
    NAME = "PausedPipeline"

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_{}".format(self.NAME)) as cass:
            return cass, manager.unpause(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{name}/unpause'.format(name=self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    def test_unpause(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/unpause_{}_complex".format(self.NAME)):
            manager.pause(self.NAME, '')

            result = manager.unpause(self.NAME)
            assert result is None

            expected_items = {'paused': False, 'schedulable': True, 'locked': False}
            status = manager.status(self.NAME)
            for name, value in expected_items.items():
                assert status[name] == value


class TestReleaseLock(BaseTestPipelineManager, AbstractTestManager, ReturnValueMixin, ConfirmHeaderMixin):
    NAME = "Deploy_UAT"

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/release_lock") as cass:
            return cass, manager.release_lock(self.NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/pipelines/{name}/releaseLock'.format(name=self.NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        return 'pipeline lock released for {0}\n'.format(self.NAME)


@pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
@pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
class TestSchedule(
    BaseTestPipelineManager,
    AbstractTestManager,
    RequestContentTypeHeadersMixin,
    ReturnValueMixin,
    ConfirmHeaderMixin
):
    NAME = "TestSchedule"

    @pytest.fixture()
    def suffix(self, variables, secure_variables):
        return self.get_suffix(variables, secure_variables)

    @pytest.fixture()
    def _execute_test_action(self, suffix, variables, secure_variables, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/schedule-{0}".format(suffix)) as cass:
            return cass, manager.schedule(
                name='{0}-{1}'.format(self.NAME, suffix),
                variables=variables,
                secure_variables=secure_variables
            )

    @pytest.fixture()
    def expected_request_url(self, suffix, variables, secure_variables):
        return '/go/api/pipelines/{name}/schedule'.format(
            name='{0}-{1}'.format(self.NAME, suffix)
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_content_type_headers(self, *args, **kwargs):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self, suffix):
        return 'Request to schedule pipeline {0}-{1} accepted\n'.format(self.NAME, suffix)

    # Have to override and call super, as we're putting parameters to the class
    # and they are applied to parent classes. As there are two classes for which
    # we putting that parameters, we got an error from py.test `ValueError: duplicate 'variables'`

    def test_request_url(self, _execute_test_action, expected_request_url):
        return super(self.__class__, self).test_request_url(_execute_test_action, expected_request_url)

    def test_request_method(self, _execute_test_action, expected_request_method):
        return super(self.__class__, self).test_request_method(_execute_test_action, expected_request_method)

    def test_request_accept_headers(self, _execute_test_action, expected_accept_headers):
        return super(self.__class__, self).test_request_accept_headers(_execute_test_action, expected_accept_headers)

    def test_response_code(self, _execute_test_action, expected_response_code):
        return 202

    def test_update_request_content_type_headers(self, _execute_test_action, expected_content_type_headers):
        return super(self.__class__, self).test_update_request_content_type_headers(
            _execute_test_action, expected_content_type_headers)

    def test_return_type(self, _execute_test_action, expected_return_type):
        return super(self.__class__, self).test_return_type(_execute_test_action, expected_return_type)

    def test_return_value(self, _execute_test_action, expected_return_value):
        return super(self.__class__, self).test_return_value(_execute_test_action, expected_return_value)

    def test_confirm_header(self, _execute_test_action):
        return super(self.__class__, self).test_confirm_header(_execute_test_action)


@pytest.mark.parametrize("variables", [None, {'MY_VARIABLE': 'some value'}])
@pytest.mark.parametrize("secure_variables", [None, {'MY_SECRET_VARIABLE': 'secret variable'}])
class TestScheduleWithInstance(
    BaseTestPipelineManager,
    AbstractTestManager,
    ReturnValueMixin
):
    EXPECTED_CASSETTE_COUNT = None
    NAME = "TestScheduleWithInstance"

    variables = [None, {'MY_VARIABLE': 'some value'}]
    secure_variables = [None, {'MY_SECRET_VARIABLE': 'secret variable'}]

    @pytest.fixture()
    def suffix(self, variables, secure_variables):
        return self.get_suffix(variables, secure_variables)

    @pytest.fixture()
    def pipeline_name(self, suffix):
        return '{0}-{1}'.format(self.NAME, suffix)

    @pytest.fixture()
    def _execute_test_action(self, suffix, pipeline_name, variables, secure_variables, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/schedule-instance-{0}".format(suffix)) as cass:
            if not len(cass.requests):
                with my_vcr.use_cassette("pipeline/schedule-instance-prepare-{0}".format(suffix)):
                    pipeline_instance = manager.last(pipeline_name)
                    while pipeline_instance and not pipeline_instance.data.can_run:
                        print("Sleeping...")  # noqa
                        time.sleep(10)
                        pipeline_instance = manager.last(pipeline_name)

                    backoff = 4
                    max_tries = 50
            else:
                backoff = 0
                max_tries = 20

            return cass, manager.schedule_with_instance(
                name=pipeline_name,
                variables=variables,
                secure_variables=secure_variables,
                backoff=backoff,
                max_tries=max_tries
            )

    @pytest.fixture()
    def expected_request_url(self, suffix, variables, secure_variables):
        return '/go/api/pipelines/{name}/history/0'.format(
            name='{0}-{1}'.format(self.NAME, suffix)
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return pipeline.PipelineInstance

    @pytest.fixture()
    def expected_return_value(self, suffix):
        pytest.skip()

    # Have to override and call super, as we're putting parameters to the class
    # and they are applied to parent classes. As there are two classes for which
    # we putting that parameters, we got an error from py.test `ValueError: duplicate 'variables'`

    def test_request_url(self, _execute_test_action, expected_request_url):
        return super(self.__class__, self).test_request_url(_execute_test_action, expected_request_url)

    def test_request_method(self, _execute_test_action, expected_request_method):
        return super(self.__class__, self).test_request_method(_execute_test_action, expected_request_method)

    def test_request_accept_headers(self, _execute_test_action, expected_accept_headers):
        return super(self.__class__, self).test_request_accept_headers(_execute_test_action, expected_accept_headers)

    def test_response_code(self, _execute_test_action, expected_response_code):
        return super(self.__class__, self).test_response_code(_execute_test_action, expected_response_code)

    def test_return_type(self, _execute_test_action, expected_return_type):
        return super(self.__class__, self).test_return_type(_execute_test_action, expected_return_type)

    def test_return_value(self, _execute_test_action, expected_return_value):
        return super(self.__class__, self).test_return_value(_execute_test_action, expected_return_value)


class TestValueStreamMap(BaseTestPipelineManager, AbstractTestManager, ReturnValueMixin):
    NAME = 'Automated_Tests'
    COUNTER = 7

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline/value_stream_map") as cass:
            return cass, manager.value_stream_map(self.NAME, self.COUNTER)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/pipelines/value_stream_map/{name}/{counter}.json'.format(name=self.NAME, counter=self.COUNTER)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert len(result) > 0
            assert all(isinstance(i, (pipeline.PipelineInstance, material.ModificationEntity)) for i in result)

        return check_value

    def test_stages(self, _execute_test_action):
        _, result = _execute_test_action
        for item in result:
            assert hasattr(item, 'data')
            if isinstance(item, pipeline.PipelineInstance):
                assert all(isinstance(s, dict) for s in item.data.stages)
                assert all(isinstance(s, stage.StageInstance) for s in item.stages())


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.pipeline.PipelineManager.find')
    def test_indexed_based_access(self, find_mock, manager):
        name = mock.MagicMock()
        _ = manager[name]  # noqa
        find_mock.assert_called_once_with(name=name)

    @mock.patch('yagocd.resources.pipeline.PipelineManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
