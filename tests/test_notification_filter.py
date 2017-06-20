#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# The MIT License
#
# Copyright (c) 2017 Grigory Chernyshev
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

from tests import AbstractTestManager, ReturnValueMixin
from yagocd.resources import notification_filter


@pytest.fixture()
def manager(session_fixture):
    return notification_filter.NotificationFilterManager(session=session_fixture)


class BaseManager(AbstractTestManager):
    @pytest.fixture()
    def prepare_notification_filters(self, manager, my_vcr):
        with my_vcr.use_cassette("notification_filters/prepare"):
            manager.create(
                pipeline='[Any Pipeline]',
                stage='[Any Stage]',
                event='All',
            )

            manager.create(
                pipeline='[Any Pipeline]',
                stage='Dummy',
                event='All',
            )


class TestList(BaseManager, ReturnValueMixin):
    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_notification_filters):
        with my_vcr.use_cassette("notification_filters/list") as cass:
            return cass, manager.list()

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/notification_filters'

    @pytest.fixture()
    def expected_request_method(self):
        return 'GET'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(i, notification_filter.NotificationFilter) for i in result)
            assert len(result) == 2

        return check_value


class TestCreate(BaseManager, ReturnValueMixin):
    PARAMS = dict(
        pipeline='[Any Pipeline]',
        stage='foobar',
        event='All',
    )

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr):
        with my_vcr.use_cassette("notification_filters/create") as cass:
            return cass, manager.create(**self.PARAMS)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/notification_filters'

    @pytest.fixture()
    def expected_request_method(self):
        return 'POST'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(i, notification_filter.NotificationFilter) for i in result)
            assert len(result) == 3

        return check_value


class TestDelete(BaseManager, ReturnValueMixin):
    ID = '1'

    @pytest.fixture()
    def _execute_test_action(self, manager, my_vcr, prepare_notification_filters):
        with my_vcr.use_cassette("notification_filters/delete") as cass:
            return cass, manager.delete(self.ID)

    @pytest.fixture()
    def expected_request_url(self):
        return '/go/api/notification_filters/{}'.format(self.ID)

    @pytest.fixture()
    def expected_request_method(self):
        return 'DELETE'

    @pytest.fixture()
    def expected_return_type(self):
        return list

    @pytest.fixture()
    def expected_return_value(self):
        def check_value(result):
            assert all(isinstance(i, notification_filter.NotificationFilter) for i in result)
            assert len(result) == 2

        return check_value


class TestMagicMethods(object):
    @mock.patch('yagocd.resources.notification_filter.NotificationFilterManager.list')
    def test_iterator_access(self, list_mock, manager):
        for _ in manager:
            pass
        list_mock.assert_called_once_with()
