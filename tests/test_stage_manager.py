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
from yagocd.resources import stage

import pytest
import mock
from six import string_types


class BaseTestStageManager(object):
    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = 7
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'

    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return stage.StageManager(
            session=session,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER
        )


class TestCancel(BaseTestStageManager):
    def test_cancel_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_cancel") as cass:
            manager.cancel()
            assert cass.requests[0].path == '/go/api/stages/{pipeline_name}/{stage_name}/cancel'.format(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME
            )

    def test_cancel_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_cancel") as cass:
            manager.cancel()
            assert cass.requests[0].method == 'POST'

    def test_cancel_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_cancel") as cass:
            manager.cancel()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_cancel_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_cancel") as cass:
            manager.cancel()
            assert cass.responses[0]['status']['code'] == 200

    def test_cancel_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_cancel"):
            result = manager.cancel()
            assert isinstance(result, string_types)

    def test_cancel_return_value(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_cancel"):
            result = manager.cancel()
            assert result == 'Stage cancelled successfully.\n'


class TestGet(BaseTestStageManager):
    def test_get_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_get") as cass:
            manager.get()
            assert cass.requests[0].path == (
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

    def test_get_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_get") as cass:
            manager.get()
            assert cass.requests[0].method == 'GET'

    def test_get_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_get") as cass:
            manager.get()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_get_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_get") as cass:
            manager.get()
            assert cass.responses[0]['status']['code'] == 200

    def test_get_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_get"):
            result = manager.get()
            assert isinstance(result, stage.StageInstance)


class TestHistory(BaseTestStageManager):
    def test_history_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_history") as cass:
            manager.history()
            assert cass.requests[0].path == '/go/api/stages/{pipeline_name}/{stage_name}/history/{offset}'.format(
                pipeline_name=self.PIPELINE_NAME,
                stage_name=self.STAGE_NAME,
                offset=0
            )

    def test_history_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_history") as cass:
            manager.history()
            assert cass.requests[0].method == 'GET'

    def test_history_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_history") as cass:
            manager.history()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_history_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_history") as cass:
            manager.history()
            assert cass.responses[0]['status']['code'] == 200

    def test_history_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("stage/stage_history"):
            result = manager.history()
            assert all(isinstance(s, stage.StageInstance) for s in result)


class TestFullHistory(BaseTestStageManager):
    @mock.patch('yagocd.resources.stage.StageManager.history')
    def test_history_is_called(self, history_mock, manager):
        history_mock.side_effect = [['foo', 'bar', 'baz'], []]

        list(manager.full_history(self.PIPELINE_NAME, self.STAGE_NAME))

        calls = [mock.call(self.PIPELINE_NAME, self.STAGE_NAME, 0), mock.call(self.PIPELINE_NAME, self.STAGE_NAME, 3)]
        history_mock.assert_has_calls(calls)
