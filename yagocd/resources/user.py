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
from yagocd.resources import BaseManager, Base


class UserManager(BaseManager):
    """
    The users API allows users with administrator role to manage users.
    """

    def list(self):
        """
        Lists all available users.
        :return: an array of user objects :class:`yagocd.resources.user.UserEntity`.
        :rtype: yagocd.resources.user.UserEntity
        """
        response = self._session.get(
            path='{base_api}/users'.format(base_api=self.base_api),
        )

        users = list()
        for data in response.json().get('_embedded', {}).get('users', {}):
            users.append(UserEntity(session=self._session, data=data))

        return users

    def get(self, login):
        """
        Gets a user by its login name.

        :param login: login name.
        :return: a user object :class:`yagocd.resources.user.UserEntity`.
        :rtype: yagocd.resources.user.UserEntity
        """
        response = self._session.get(
            path='{base_api}/users/{login}'.format(
                base_api=self.base_api,
                login=login
            ),
        )

        return UserEntity(session=self._session, data=response.json())

    def create(self, options):
        """
        Creates a user.

        Can't make this one work: returns 404 all the time.

        :param options: dictionary of parameters for creating a user.
        :return: a user object :class:`yagocd.resources.user.UserEntity`.
        :rtype: yagocd.resources.user.UserEntity
        """
        response = self._session.post(
            path='{base_api}/users'.format(
                base_api=self.base_api
            ),
            data=json.dumps(options),
            headers={
                'Content-Type': 'application/json'
            }
        )

        return response.text

    def update(self, login, options):
        """
        Update some attributes of a user.

        :param login: login name.
        :param options: dictionary of parameters for updating a user.
        :return: the updated user object :class:`yagocd.resources.user.UserEntity`.
        :rtype: yagocd.resources.user.UserEntity
        """
        response = self._session.patch(
            path='{base_api}/users/{login}'.format(
                base_api=self.base_api,
                login=login
            ),
            data=json.dumps(options),
            headers={
                'Content-Type': 'application/json'
            }
        )

        return UserEntity(session=self._session, data=response.json())

    def delete(self, login):
        """
        Deletes a user.
        :param login: login name.
        :return: a message confirmation if the user was deleted.
        """
        response = self._session.delete(
            path='{base_api}/users/{login}'.format(
                base_api=self.base_api,
                login=login
            ),
        )

        return response.json().get('message')


class UserEntity(Base):
    """
    The user object.
    """
    pass
