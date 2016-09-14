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
import json
import os
from distutils.version import LooseVersion

import pytest
from mock import mock
from six import string_types

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import pipeline_config


@pytest.fixture()
def manager(session_fixture):
    return pipeline_config.PipelineConfigManager(session=session_fixture)


class BaseTestPipelineConfigManager(AbstractTestManager):
    @pytest.fixture()
    def expected_accept_headers(self, server_version):
        if LooseVersion(server_version) <= LooseVersion('16.6.0'):
            return 'application/vnd.go.cd.v1+json'
        else:
            return 'application/vnd.go.cd.v2+json'


class TestGet(BaseTestPipelineConfigManager, ReturnValueMixin):
    PIPELINE_NAME = 'Shared_Services'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/get_{}".format(self.PIPELINE_NAME)) as cass:
            return cass, manager.get(self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/pipelines/{}'.format(self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        pytest.skip()


class TestEdit(BaseTestPipelineConfigManager, ReturnValueMixin):
    PIPELINE_NAME = 'ParametrizedPipeline'
    NEW_LABEL = '${COUNT}-some-new-value'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_prepare_{}".format(self.PIPELINE_NAME)):
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL

        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)) as cass:
            return cass, manager.edit(original, etag, self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/pipelines/{}'.format(self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'PUT'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            new_config, new_etag = result
            assert new_config.label_template == self.NEW_LABEL

        return check_value


class TestCreate(BaseTestPipelineConfigManager, ReturnValueMixin):
    PIPELINE_NAME = 'Spam_foo_bar'

    @pytest.fixture()
    def new_config_data(self, tests_dir):
        path = os.path.join(tests_dir, 'fixtures/resources/pipeline_config/new_pipeline_payload.json')
        return json.load(open(path))

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)) as cass:
            return cass, manager.create(new_config_data)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/pipelines'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        def check_types(result):
            assert isinstance(result, tuple)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], str)

        return check_types

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            new_config, new_etag = result
            assert new_config.name == self.PIPELINE_NAME

        return check_value


class TestDelete(BaseTestPipelineConfigManager, ReturnValueMixin):
    PIPELINE_NAME = 'Spam_foo_bar'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)) as cass:
            return cass, manager.delete(self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/admin/pipelines/{}'.format(self.PIPELINE_NAME)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return string_types

    @pytest.fixture()
    def expected_return_value(self):
        return "Pipeline '{}' was deleted successfully.".format(self.PIPELINE_NAME)


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.pipeline_config.PipelineConfigManager.get')
    def test_indexed_based_access(self, get_mock, manager):
        name = mock.MagicMock()
        _ = manager[name]  # noqa
        get_mock.assert_called_once_with(pipeline_name=name)
