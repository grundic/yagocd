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

from yagocd.resources.base import Base
from yagocd.resources.artifact import ArtifactManager
from yagocd.resources.property import PropertyManager


class JobInstance(Base):
    def __init__(self, session, data, stage):
        super(JobInstance, self).__init__(session, data)
        self._stage = stage

    @property
    def pipeline_name(self):
        if 'pipeline_name' in self.data:
            return self.data.get('pipeline_name')
        elif self.stage.pipeline is not None:
            return self.stage.pipeline.data.name
        else:
            return self.stage.data.pipeline_name

    @property
    def pipeline_counter(self):
        if 'pipeline_counter' in self.data:
            return self.data.get('pipeline_counter')
        elif self.stage.pipeline is not None:
            return self.stage.pipeline.data.counter
        else:
            return self.stage.data.pipeline_counter

    @property
    def stage_name(self):
        if 'stage_name' in self.data:
            return self.data.get('stage_name')
        else:
            return self.stage.data.name

    @property
    def stage_counter(self):
        if 'stage_counter' in self.data:
            return self.data.get('stage_counter')
        else:
            return self.stage.data.counter

    @property
    def stage(self):
        return self._stage

    @property
    def artifact(self):
        return ArtifactManager(
            session=self._session,
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.stage_name,
            stage_counter=self.stage_counter,
            job_name=self.data.name
        )

    @property
    def property(self):
        return PropertyManager(
            session=self._session,
            pipeline_name=self.pipeline_name,
            pipeline_counter=self.pipeline_counter,
            stage_name=self.stage_name,
            stage_counter=self.stage_counter,
            job_name=self.data.name
        )


if __name__ == '__main__':
    pass
