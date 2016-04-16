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

from yagocd.resources import BaseManager


class FeedManager(BaseManager):
    def pipelines(self):
        response = self._session.get(
            path='{base_api}/pipelines.xml'.format(base_api=self.base_api),
            headers={'Accept': 'application/xml'},
        )

        return response.text

    def pipeline_by_id(self, pipeline_id):
        response = self._session.get(
            path='{base_api}/pipelines/{pipeline_name}/{pipeline_id}.xml'.format(
                base_api=self.base_api,
                pipeline_name='THIS_PARAMETER_IS_USELESS',  # WTF?!!
                pipeline_id=pipeline_id,
            ),
            headers={'Accept': 'application/xml'},
        )

        return response.text

    def stages(self, pipeline_name):
        response = self._session.get(
            path='{base_api}/pipelines/{pipeline_name}/stages.xml'.format(
                base_api=self.base_api,
                pipeline_name=pipeline_name
            ),
            headers={'Accept': 'application/xml'},
        )

        return response.text

    def stage_by_id(self, stage_id):
        response = self._session.get(
            path='{base_api}/stages/{stage_id}.xml'.format(
                base_api=self.base_api,
                stage_id=stage_id
            ),
            headers={'Accept': 'application/xml'},
        )

        return response.text

    def stage(self, pipeline_name, pipeline_counter, stage_name, stage_counter):
        response = self._session.get(
            path='{base_api}/pipelines/{pipeline_name}/{pipeline_counter}/{stage_name}/{stage_counter}.xml'.format(
                base_api=self._session.base_api(api_path=''),  # WTF?!!
                pipeline_name=pipeline_name,
                pipeline_counter=pipeline_counter,
                stage_name=stage_name,
                stage_counter=stage_counter,
            ),
            headers={'Accept': 'application/xml'},
        )

        return response.text

    def job_by_id(self, job_id):
        response = self._session.get(
            path='{base_api}/jobs/{job_id}.xml'.format(
                base_api=self.base_api,
                job_id=job_id
            ),
            headers={'Accept': 'application/xml'},
        )

        return response.text


if __name__ == '__main__':
    pass
