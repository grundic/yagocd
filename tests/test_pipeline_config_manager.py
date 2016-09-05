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

from yagocd.resources import pipeline_config


class BaseTestPipelineConfigManager(object):
    @pytest.fixture()
    def manager(self, session_fixture):
        return pipeline_config.PipelineConfigManager(session=session_fixture)

    @staticmethod
    def _expected_accept_header(manager):
        if LooseVersion(manager._session.server_version) <= '16.6.0':
            return 'application/vnd.go.cd.v1+json'
        else:
            return 'application/vnd.go.cd.v2+json'

    def test_cache_server_version(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/server_version_cache"):
            assert manager._session.server_version


class TestGet(BaseTestPipelineConfigManager):
    PIPELINE_NAME = 'Shared_Services'

    def test_get_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/get_{}".format(self.PIPELINE_NAME)) as cass:
            manager.get(self.PIPELINE_NAME)
            assert cass.requests[0].path == '/go/api/admin/pipelines/{}'.format(self.PIPELINE_NAME)

    def test_get_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/get_{}".format(self.PIPELINE_NAME)) as cass:
            manager.get(self.PIPELINE_NAME)
            assert cass.requests[0].method == 'GET'

    def test_get_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/get_{}".format(self.PIPELINE_NAME)) as cass:
            manager.get(self.PIPELINE_NAME)
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_get_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/get_{}".format(self.PIPELINE_NAME)) as cass:
            manager.get(self.PIPELINE_NAME)
            assert cass.responses[0]['status']['code'] == 200

    def test_get_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/get_{}".format(self.PIPELINE_NAME)):
            result = manager.get(self.PIPELINE_NAME)
            assert isinstance(result, tuple)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], str)


class TestEdit(BaseTestPipelineConfigManager):
    PIPELINE_NAME = 'ParametrizedPipeline'
    NEW_LABEL = '${COUNT}-some-new-value'

    def test_edit_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)) as cass:
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL
            manager.edit(original, etag, self.PIPELINE_NAME)
            assert cass.requests[1].path == '/go/api/admin/pipelines/{}'.format(self.PIPELINE_NAME)

    def test_edit_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)) as cass:
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL
            manager.edit(original, etag, self.PIPELINE_NAME)
            assert cass.requests[1].method == 'PUT'

    def test_edit_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)) as cass:
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL
            manager.edit(original, etag, self.PIPELINE_NAME)
            assert cass.requests[1].headers['accept'] == self._expected_accept_header(manager)

    def test_edit_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)) as cass:
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL
            manager.edit(original, etag, self.PIPELINE_NAME)
            assert cass.responses[1]['status']['code'] == 200

    def test_edit_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)):
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL
            result = manager.edit(original, etag, self.PIPELINE_NAME)

            assert isinstance(result, tuple)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], str)

    def test_edit_return_value(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/edit_{}".format(self.PIPELINE_NAME)):
            original, etag = manager.get(self.PIPELINE_NAME)
            original.label_template = self.NEW_LABEL
            new_config, new_etag = manager.edit(original, etag, self.PIPELINE_NAME)

            assert new_config.label_template == self.NEW_LABEL


class TestCreate(BaseTestPipelineConfigManager):
    PIPELINE_NAME = 'Spam_foo_bar'

    @pytest.fixture()
    def new_config_data(self, tests_dir):
        path = os.path.join(tests_dir, 'fixtures/resources/pipeline_config/new_pipeline_payload.json')
        return json.load(open(path))

    def test_create_request_url(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)) as cass:
            manager.create(new_config_data)
            assert cass.requests[0].path == '/go/api/admin/pipelines'

    def test_create_request_method(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)) as cass:
            manager.create(new_config_data)
            assert cass.requests[0].method == 'POST'

    def test_create_request_accept_headers(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)) as cass:
            manager.create(new_config_data)
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_create_response_code(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)) as cass:
            manager.create(new_config_data)
            assert cass.responses[0]['status']['code'] == 200

    def test_create_return_type(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)):
            result = manager.create(new_config_data)

            assert isinstance(result, tuple)
            assert isinstance(result[0], dict)
            assert isinstance(result[1], str)

    def test_create_return_value(self, manager, my_vcr, new_config_data):
        with my_vcr.use_cassette("pipeline_config/create_{}".format(self.PIPELINE_NAME)):
            new_config, new_etag = manager.create(new_config_data)

            assert new_config.name == self.PIPELINE_NAME


class TestDelete(BaseTestPipelineConfigManager):
    PIPELINE_NAME = 'Spam_foo_bar'

    def _perform_action(self, manager):
        if hasattr(manager.delete, 'since_version'):
            since_version = manager.delete.since_version
            server_version = manager._session.server_version
            if LooseVersion(server_version) < since_version:
                pytest.skip("Method `{name}` is not supported on '{server_version}'".format(
                    name=manager.delete.__name__, server_version=server_version
                ))
        return manager.delete(self.PIPELINE_NAME)

    def test_delete_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)) as cass:
            self._perform_action(manager)
            assert cass.requests[0].path == '/go/api/admin/pipelines/{}'.format(self.PIPELINE_NAME)

    def test_delete_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)) as cass:
            self._perform_action(manager)
            assert cass.requests[0].method == 'DELETE'

    def test_delete_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)) as cass:
            self._perform_action(manager)
            assert cass.requests[0].headers['accept'] == self._expected_accept_header(manager)

    def test_delete_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)) as cass:
            self._perform_action(manager)
            assert cass.responses[0]['status']['code'] == 200

    def test_delete_return_type(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)):
            result = self._perform_action(manager)

            assert isinstance(result, str)

    def test_delete_return_value(self, manager, my_vcr):
        with my_vcr.use_cassette("pipeline_config/delete_{}".format(self.PIPELINE_NAME)):
            result = self._perform_action(manager)

            assert result == "Pipeline '{}' was deleted successfully.".format(self.PIPELINE_NAME)
