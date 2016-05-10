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

import os
import sys
import time
import subprocess

import mock
import pytest
import requests
from vcr import VCR


@pytest.fixture(scope='session')
def tests_dir():
    return os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def mock_session():
    session = mock.patch('yagocd.session.Session').start()
    session.server_url = 'http://example.com'
    return session


@pytest.fixture()
def my_vcr():
    return VCR(
        path_transformer=VCR.ensure_suffix('.yaml'),
        cassette_library_dir=os.path.join(tests_dir(), 'fixtures/cassettes'),
    )


CONTAINER_NAME = 'yagocd-server'
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


def start_container():
    output = subprocess.check_output([
        "/usr/local/bin/docker",
        "ps",
        "--quiet",
        "--filter=name={container_name}".format(
            container_name=CONTAINER_NAME),
    ])

    if not output:
        subprocess.check_call([
            "/usr/local/bin/docker",
            "run",
            "--detach",
            "--net=host",
            "--volume={current_dir}/docker:/workspace".format(
                current_dir=CURRENT_DIR
            ),
            "--workdir=/workspace",
            "--name={container_name}".format(
                container_name=CONTAINER_NAME
            ),
            "gocd/gocd-dev",
            "/bin/bash",
            "-c",
            "'/workspace/bootstrap.sh'",
        ])


def wait_till_started():
    while True:
        try:
            requests.get("http://local.docker:8153/go")
        except requests.exceptions.ConnectionError:
            sys.stdout.write('.')
            time.sleep(5)
        else:
            break


def stop_container():
    subprocess.check_call([
        "/usr/local/bin/docker",
        "rm",
        "-f",
        CONTAINER_NAME
    ])


@pytest.fixture(scope="session")
def gocd_docker(request):
    start_container()
    wait_till_started()

    def fin():
        stop_container()

    request.addfinalizer(fin)
