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

from yagocd.resources import agent
from yagocd.resources import Base
import pytest


class TestAgentEntity(object):
    @pytest.fixture()
    def agent_entity(self, mock_session):
        data = json.load(open('tests/fixtures/resources/agent/68e5d48c-753a-4395-a79c-1cb22d77a12f.json'))
        return agent.AgentEntity(session=mock_session, data=data)

    def test_instance_is_not_none(self, agent_entity):
        assert agent_entity is not None

    def test_is_instance_of_base(self, agent_entity):
        assert isinstance(agent_entity, Base)
