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
from mock import mock
from six import string_types
from six.moves.urllib.parse import urlencode

from tests import AbstractTestManager, ConfirmHeaderMixin, ReturnValueMixin
from yagocd.resources import property


class BaseTestPropertyManager(object):
    PIPELINE_NAME = 'Shared_Services'
    PIPELINE_COUNTER = 7
    STAGE_NAME = 'Commit'
    STAGE_COUNTER = '1'
    JOB_NAME = 'build'

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

    @pytest.fixture()
    def mock_manager(self, mock_session):
        return property.PropertyManager(
            session=mock_session,
            pipeline_name=self.PIPELINE_NAME,
            pipeline_counter=self.PIPELINE_COUNTER,
            stage_name=self.STAGE_NAME,
            stage_counter=self.STAGE_COUNTER,
            job_name=self.JOB_NAME
        )


class TestList(AbstractTestManager, BaseTestPropertyManager, ReturnValueMixin):
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


class TestGet(AbstractTestManager, BaseTestPropertyManager, ReturnValueMixin):
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
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestHistorical(AbstractTestManager, BaseTestPropertyManager, ReturnValueMixin):
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


class TestCreate(AbstractTestManager, BaseTestPropertyManager, ReturnValueMixin, ConfirmHeaderMixin):
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


class TestMagicMethods(BaseTestPropertyManager):
    @mock.patch('yagocd.resources.property.PropertyManager.list')
    def test_len(self, list_mock, manager):
        size = 17
        list_mock.return_value = [mock.MagicMock] * size
        assert len(manager) == size

    @mock.patch('yagocd.resources.property.PropertyManager.list')
    def test_contains(self, list_mock, manager):
        list_mock.return_value = [1, 3, 5, 7]
        assert 3 in manager
        assert 2 not in manager

    @mock.patch('yagocd.resources.property.PropertyManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        name = mock.MagicMock()
        _ = manager[name]  # noqa
        get_mock.assert_called_once_with(name=name)

    @mock.patch('yagocd.resources.property.PropertyManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()


@mock.patch('yagocd.resources.property.PropertyManager.list')
class TestDictionaryMethods(BaseTestPropertyManager):
    def test_keys(self, list_mock, mock_manager):
        expected = mock.MagicMock(name='list')
        list_mock.return_value.keys.return_value = expected
        assert mock_manager.keys() == expected

    def test_values(self, list_mock, mock_manager):
        expected = mock.MagicMock(name='values')
        list_mock.return_value.values.return_value = expected
        assert mock_manager.values() == expected

    def test_items(self, list_mock, mock_manager):
        expected = mock.MagicMock(name='items')
        list_mock.return_value.items.return_value = expected
        assert mock_manager.items() == expected
