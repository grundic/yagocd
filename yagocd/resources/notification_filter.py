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

from yagocd.resources import Base, BaseManager
from yagocd.util import since


@since('17.5.0')
class NotificationFilterManager(BaseManager):
    """
    The notification filters API allows the authenticated user to manage their notification filters.

    `Official documentation. <https://api.go.cd/current/#the-notification-filter-object>`_

    :versionadded: 17.5.0.
    """

    RESOURCE_PATH = '{base_api}/notification_filters'

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: list of yagocd.resources.notification_filter.NotificationFilter
        """
        return iter(self.list())

    def list(self):
        """
        Lists all notification filters for the authenticated user.

        :rtype: list of yagocd.resources.notification_filter.NotificationFilter
        """
        response = self._session.get(
            path=self.RESOURCE_PATH.format(base_api=self.base_api)
        )

        result = list()
        etag = response.headers['ETag']
        for data in response.json().get('filters', {}):
            result.append(NotificationFilter(session=self._session, data=data, etag=etag))

        return result

    def create(self, pipeline, stage, event, match_commits=None):
        """
        Creates a notification filter for the authenticated user.

        :param pipeline: The pipeline name to match. Can also be `[Any Pipeline]`. This attribute MUST be specified.
        :param stage: The stage name to match. Can also be `[Any Stage]`. This attribute MUST be specified.
        :param event: The event to match. Can be one of: `All`, `Passes`, `Fails`, `Breaks`, `Fixed`, `Cancelled`.
        This attribute MUST be specified.
        :param match_commits: Should the filter only match the user’s commits? Defaults to false if omitted.
        :returns: An array of notification filter objects representing the current set the user’s notification filters.
        :rtype: list of yagocd.resources.notification_filter.NotificationFilter
        """
        response = self._session.post(
            path=self.RESOURCE_PATH.format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
                'Content-Type': 'application/json',
            },
            data=json.dumps(dict(
                pipeline=pipeline,
                stage=stage,
                event=event,
                match_commits=match_commits
            )),
        )

        etag = response.headers['ETag']
        return [
            NotificationFilter(session=self._session, data=data, etag=etag)
            for data in response.json().get('filters', {})
        ]

    def delete(self, filter_id):
        """
        Deletes a notification filter for the authenticated user.

        :param filter_id: id of the notification filter to delete.
        :return: a message if the notification filter is deleted or not.
        :rtype: str
        """

        response = self._session.delete(
            self._session.urljoin(self.RESOURCE_PATH, filter_id).format(base_api=self.base_api),
            headers={
                'Accept': self._accept_header(),
            },
        )

        etag = response.headers['ETag']
        return [
            NotificationFilter(session=self._session, data=data, etag=etag)
            for data in response.json().get('filters', {})
        ]


class NotificationFilter(Base):
    pass
