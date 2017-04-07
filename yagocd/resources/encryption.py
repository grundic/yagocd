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
import json

from yagocd.resources import BaseManager
from yagocd.util import since


@since('17.1.0')
class EncryptionManager(BaseManager):
    """
    The encryption API allows users with any administrator privilege 
    to get the cipher text(encrypted text) corresponding to any plain 
    text value. You may use this cipher text in other APIs that allow 
    you to configure the pipelines and templates.
    
    :warning: This API is rate limited to 30 requests per minute to 
    prevent brute force attacks that may allow attackers to guess the 
    cipher key

    `Official documentation. <https://api.go.cd/current/#encryption>`_

    :versionadded: 17.1.0.
    """

    RESOURCE_PATH = '{base_api}/admin/encrypt'

    def encrypt(self, value):
        """
        Returns the encrypted value for the plain text passed.

        :param value: string value to encrypt.
        :rtype: str
        """
        response = self._session.post(
            path=self._session.urljoin(self.RESOURCE_PATH).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
            },
            data=json.dumps({'value': value})
        )

        return response.json()['encrypted_value']
