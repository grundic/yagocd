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
from yagocd.resources import configuration

import pytest


class BaseTestConfigurationManager(object):
    @pytest.fixture()
    def session(self):
        return Session(auth=None, options=Yagocd.DEFAULT_OPTIONS)

    @pytest.fixture()
    def manager(self, session):
        return configuration.ConfigurationManager(session=session)


class TestModifications(BaseTestConfigurationManager):
    def test_modifications_request_url(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.requests[0].path == '/go/api/config/revisions'

    def test_modifications_request_method(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.requests[0].method == 'GET'

    def test_modifications_request_accept_headers(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.requests[0].headers['accept'] == 'application/json'

    def test_modifications_response_code(self, manager, my_vcr):
        with my_vcr.use_cassette("configuration/modifications") as cass:
            manager.modifications()
            assert cass.responses[0]['status']['code'] == 200
