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

import mock
import pytest
from six import string_types

from tests import AbstractTestManager, ConfirmHeaderMixin, ReturnValueMixin
from yagocd.resources import pipeline, stage


class BaseTestStageManager(object):
    PIPELINE_NAME = 'CancelledPipeline'
    PIPELINE_COUNTER = 2
    STAGE_NAME = 'defaultStage'
    STAGE_COUNTER = '1'

    @pytest.fixture()
    def manager(self, session_fixture):
        return stage.StageManager(
            session=session_fixture,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER
        )

    @pytest.fixture()
    def mock_manager(self, mock_session):
        return stage.StageManager(
            session=mock_session,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER
        )


class TestCancel(BaseTestStageManager, AbstractTestManager, ReturnValueMixin, ConfirmHeaderMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, session_fixture):
        with my_vcr.use_cassette("stage/stage_cancel") as cass:
            if not len(cass.requests):
                with my_vcr.use_cassette("stage/schedule_with_instance"):
                    # trigger pipeline, so it could be cancelled
                    pipeline.PipelineManager(session_fixture).schedule_with_instance(self.PIPELINE_NAME)
                    while manager.last(self.PIPELINE_NAME, self.STAGE_NAME).data.result != 'Unknown':
                        time.sleep(1)

            return cass, manager.cancel()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/stages/{pipeline_name}/{stage_name}/cancel'.format(
            pipeline_name=self.PIPELINE_NAME,
            stage_name=self.STAGE_NAME
        )

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
        return 'Stage cancelled successfully.\n'


class TestGet(BaseTestStageManager, AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_get") as cass:
            return cass, manager.get()

    @pytest.fixture()
    def expected_request_url(self):
        return (
            '/go'
            '/api'
            '/stages'
            '/{pipeline_name}'
            '/{stage_name}'
            '/instance'
            '/{pipeline_counter}'
            '/{stage_counter}'
        ).format(
            pipeline_name=self.PIPELINE_NAME,
            stage_name=self.STAGE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_counter=self.STAGE_COUNTER
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return stage.StageInstance

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestHistory(BaseTestStageManager, AbstractTestManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_history") as cass:
            return cass, manager.history()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/stages/{pipeline_name}/{stage_name}/history/{offset}'.format(
            pipeline_name=self.PIPELINE_NAME,
            stage_name=self.STAGE_NAME,
            offset=0
        )

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
            all(isinstance(s, stage.StageInstance) for s in result)

        return check_value


class TestFullHistory(BaseTestStageManager):
    @mock.patch('yagocd.resources.stage.StageManager.history')
    def test_history_is_called(self, history_mock, mock_manager):
        history_mock.side_effect = [['foo', 'bar', 'baz'], []]

        list(mock_manager.full_history(self.PIPELINE_NAME, self.STAGE_NAME))

        calls = [mock.call(self.PIPELINE_NAME, self.STAGE_NAME, 0), mock.call(self.PIPELINE_NAME, self.STAGE_NAME, 3)]
        history_mock.assert_has_calls(calls)


class TestLast(BaseTestStageManager):
    @mock.patch('yagocd.resources.stage.StageManager.history')
    def test_history_is_called(self, history_mock, mock_manager):
        history_mock.side_effect = [['foo', 'bar', 'baz'], []]

        result = mock_manager.last()
        history_mock.assert_called()
        assert result == 'foo'
