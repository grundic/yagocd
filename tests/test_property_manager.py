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
from six import string_types
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import urlencode

from tests import AbstractTestManager, ConfirmHeaderMixin, ReturnValueMixin
from yagocd.resources import property


class BaseTestPropertyManager(AbstractTestManager):
    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = 7
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'
    JOB_NAME = 'build'

    def expected_request_url(self, *args, **kwargs):
        raise NotImplementedError()

    def expected_request_method(self, *args, **kwargs):
        raise NotImplementedError()

    def _execute_test_action(self, *args, **kwargs):
        raise NotImplementedError()

    @pytest.fixture()
    def manager(self, session_fixture):
        return property.PropertyManager(
            session=session_fixture,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME
        )


class TestList(BaseTestPropertyManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return (
            '/go'
            '/properties'
            '/{pipeline_name}'
            '/{pipeline_counter}'
            '/{stage_name}'
            '/{stage_counter}'
            '/{job_name}'
        ).format(
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME
        )

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
        pytest.skip()


class TestGet(BaseTestPropertyManager, ReturnValueMixin):
    PROPERTY_NAME = 'cruise_pipeline_counter'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_get") as cass:
            return cass, manager.get(self.PROPERTY_NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return (
            '/go'
            '/properties'
            '/{pipeline_name}'
            '/{pipeline_counter}'
            '/{stage_name}'
            '/{stage_counter}'
            '/{job_name}'
            '/{property_name}'
        ).format(
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME,
            property_name=self.PROPERTY_NAME
        )

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
        pytest.skip()


class TestHistorical(BaseTestPropertyManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_historical") as cass:
            return cass, manager.historical()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/properties/search'

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
        pytest.skip()

    def test_request_params(self, _execute_test_action):
        cass, result = _execute_test_action
        assert cass.requests[0].query == [
            ('jobName', self.JOB_NAME),
            ('pipelineName', self.PIPELINE_NAME),
            ('stageName', self.STAGE_NAME)
        ]


class TestCreate(BaseTestPropertyManager, ReturnValueMixin, ConfirmHeaderMixin):
    PROPERTY_NAME = 'foo_bar_baz'
    PROPERTY_VALUE = 100500

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create") as cass:
            return cass, manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)

    @pytest.fixture()
    def expected_request_url(self):
        return (
            '/go'
            '/properties'
            '/{pipeline_name}'
            '/{pipeline_counter}'
            '/{stage_name}'
            '/{stage_counter}'
            '/{job_name}'
            '/{property_name}'
        ).format(
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME,
            property_name=self.PROPERTY_NAME
        )

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_response_code(self, *args, **kwargs):
        return 201

    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        return 'application/json'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()

    def test_request_params(self, _execute_test_action):
        cass, result = _execute_test_action
        assert cass.requests[0].body.decode('ascii') == urlencode({'value': self.PROPERTY_VALUE})
