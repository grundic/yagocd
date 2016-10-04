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


class YagocdException(Exception):
    """
    Base class for custom exceptions.
    """


class RequestError(YagocdException):
    """
    Exception for throwing on request errors.

    Usually extended error information would be contained in response as json object.
    """

    def __init__(self, summary, response):
        self.summary = summary
        # noinspection PyBroadException
        try:
            self.json = response.json()
        except:
            self.json = {}

    def __str__(self):
        msg = self.summary
        reason = self.json.get('message')
        if reason:
            msg += '\n  Reason: {}'.format(reason)

        errors = self.json.get('data', {}).get('errors', {})
        for field, field_errors in errors.items():
            for field_error in field_errors:
                msg += '\n  {}: {}'.format(field, field_error)

        error = self.json.get('error')
        if error:
            msg += '\n  {}'.format(error)

        return msg
