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
from yagocd.resources import Base, BaseManager
from yagocd.util import since


@since('16.7.0')
class PluginInfoManager(BaseManager):
    """
    The plugin info API allows users with administrator role
    to fetch information about installed plugins.

    `Official documentation. <https://api.go.cd/current/#plugin-info>`_

    :versionadded: 16.7.0.
    """

    def __iter__(self):
        """
        Method add iterator protocol for the manager.

        :rtype: list of yagocd.resources.plugin_info.PluginInfo
        """
        return iter(self.list())

    def __getitem__(self, name):
        """
        Method add possibility to get plugin info by the name using dictionary like syntax.

        :param name: id or name of the plugin to get the info.
        :rtype: yagocd.resources.plugin_info.PluginInfo
        """
        return self.get(name=name)

    def list(self):
        """
        Lists all available plugin info.

        :rtype: list of yagocd.resources.plugin_info.PluginInfo
        """
        response = self._session.get(
            path='{base_api}/admin/plugin_info'.format(base_api=self.base_api)
        )

        result = list()
        for data in response.json().get('_embedded', {}).get('plugin_info', {}):
            result.append(PluginInfo(session=self._session, data=data))

        return result

    def get(self, name):
        """
        Gets plugin info for a specified plugin id.

        :param name: id or name of the plugin to get the info.
        :rtype: yagocd.resources.plugin_info.PluginInfo
        """
        response = self._session.get(
            path='{base_api}/admin/plugin_info/{name}'.format(
                base_api=self.base_api, name=name
            )
        )

        return PluginInfo(session=self._session, data=response.json())


class PluginInfo(Base):
    pass
