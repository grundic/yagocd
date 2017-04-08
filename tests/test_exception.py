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
from mock.mock import MagicMock

from yagocd.exception import RequestError


class TestRequestError(object):
    @pytest.mark.parametrize('summary, json, expected_str', [
        ('Some error', None, 'Some error'),
        ('Some error', '', 'Some error'),
        ('Some error', '{ non json', 'Some error'),

        ('Some error', dict(message='foobar is here'), 'Some error\n  Reason: foobar is here'),

        ('Some error', dict(error='baz is there'), 'Some error\n  baz is there'),

        (
            'Some error',
            dict(message='foobar is here', error='baz is there'),
            'Some error\n  Reason: foobar is here\n  baz is there'),

        (
            'Some error',
            dict(message='foobar is here', data=dict(errors=dict())),
            'Some error\n  Reason: foobar is here'
        ),
        (
            'Some error',
            dict(
                message='foobar is here',
                data=dict(errors=dict(field_x=['Error for field x!'], field_y=['Error for field y!']))
            ),
            [
                'Some error\n  Reason: foobar is here\n  field_x: Error for field x!\n  field_y: Error for field y!',
                'Some error\n  Reason: foobar is here\n  field_y: Error for field y!\n  field_x: Error for field x!',
            ]
        ), (
            'Some error',
            dict(
                message='foobar is here',
                data=dict(errors=dict(field_x=['Error for field x!'], field_y=['Error for field y!'])),
                error='baz is there'
            ),
            [
                (
                    'Some error\n  Reason: foobar is here'
                    '\n  field_x: Error for field x!\n  field_y: Error for field y!\n  baz is there'
                ),
                (
                    'Some error\n  Reason: foobar is here'
                    '\n  field_y: Error for field y!\n  field_x: Error for field x!\n  baz is there'
                ),
            ]
        ),
    ])
    def test_to_string(self, summary, json, expected_str):
        response = MagicMock()
        response.json.return_value = json
        error = RequestError(summary=summary, response=response)

        if isinstance(expected_str, list):
            assert any(expected == str(error) for expected in expected_str)
        else:
            assert expected_str == str(error)
