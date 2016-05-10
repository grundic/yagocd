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
from yagocd.resources import property

import pytest
from six import string_types
from six.moves.urllib.parse import urlencode


class BaseTestPropertyManager(object):
    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = 7
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'
    JOB_NAME = 'build'

    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return property.PropertyManager(
            session=session,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME
        )


class TestList(BaseTestPropertyManager):
    def test_list_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_list") as cass:
            manager.list()
            assert cass.requests[0].path == (
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

    def test_list_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_list") as cass:
            manager.list()
            assert cass.requests[0].method == 'GET'

    def test_list_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_list") as cass:
            manager.list()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_list_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_list") as cass:
            manager.list()
            assert cass.responses[0]['status']['code'] == 200

    def test_list_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_list"):
            result = manager.list()
            assert isinstance(result, dict)


class TestGet(BaseTestPropertyManager):
    PROPERTY_NAME = 'cruise_pipeline_counter'

    def test_get_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_get") as cass:
            manager.get(self.PROPERTY_NAME)
            assert cass.requests[0].path == (
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

    def test_get_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_get") as cass:
            manager.get(self.PROPERTY_NAME)
            assert cass.requests[0].method == 'GET'

    def test_get_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_get") as cass:
            manager.get(self.PROPERTY_NAME)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_get_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_get") as cass:
            manager.get(self.PROPERTY_NAME)
            assert cass.responses[0]['status']['code'] == 200

    def test_get_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_get"):
            result = manager.get(self.PROPERTY_NAME)
            assert isinstance(result, dict)


class TestHistorical(BaseTestPropertyManager):
    def test_historical_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_historical") as cass:
            manager.historical()
            assert cass.requests[0].path == '/go/properties/search'

    def test_historical_request_params(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_historical") as cass:
            manager.historical()
            assert cass.requests[0].query == [
                ('jobName', self.JOB_NAME),
                ('pipelineName', self.PIPELINE_NAME),
                ('stageName', self.STAGE_NAME)
            ]

    def test_historical_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_historical") as cass:
            manager.historical()
            assert cass.requests[0].method == 'GET'

    def test_historical_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_historical") as cass:
            manager.historical()


class TestCreate(BaseTestPropertyManager):
    PROPERTY_NAME = 'foo_bar'
    PROPERTY_VALUE = 100500

    def test_create_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create") as cass:
            manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)
            assert cass.requests[0].path == (
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

    def test_create_request_params(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create") as cass:
            manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)
            assert cass.requests[0].body.decode('ascii') == urlencode({'value': self.PROPERTY_VALUE})

    def test_create_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create") as cass:
            manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)
            assert cass.requests[0].method == 'POST'

    def test_create_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create") as cass:
            manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_create_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create") as cass:
            manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)
            assert cass.responses[0]['status']['code'] == 201

    def test_create_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("property/property_create"):
            result = manager.create(self.PROPERTY_NAME, self.PROPERTY_VALUE)
            assert isinstance(result, string_types)
