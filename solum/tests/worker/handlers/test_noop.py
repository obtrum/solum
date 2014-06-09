# Copyright 2014 - Rackspace Hosting
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from solum.openstack.common.gettextutils import _
from solum.tests import base
from solum.tests import utils
from solum.tests.worker.handlers import test_shell
from solum.worker.handlers import noop as noop_handler


class HandlerTest(base.BaseTestCase):
    def setUp(self):
        super(HandlerTest, self).setUp()
        self.ctx = utils.dummy_context()

    @mock.patch('solum.worker.handlers.noop.LOG')
    def test_echo(self, fake_LOG):
        noop_handler.Handler().echo({}, 'foo')
        fake_LOG.debug.assert_called_once_with(_('%s') % 'foo')

    @mock.patch('solum.worker.handlers.noop.LOG')
    def test_build(self, fake_LOG):
        git_info = test_shell.mock_git_info()
        args = [5, git_info, 'new_app',
                '1-2-3-4', 'heroku', 'docker', 44, None, 'fake-private-key']
        noop_handler.Handler().build(self.ctx, *args)
        message = 'Build %s %s %s %s %s %s %s %s %s' % tuple(args)
        fake_LOG.debug.assert_called_once_with(_("%s") % message)

    @mock.patch('solum.worker.handlers.noop.LOG')
    def test_unittest(self, fake_LOG):
        git_info = test_shell.mock_git_info()
        args = [5, git_info, 'pep8', 'fake-private-key']
        noop_handler.Handler().unittest(self.ctx, *args)
        message = 'Unittest %s %s %s %s' % tuple(args)
        fake_LOG.debug.assert_called_once_with(_("%s") % message)
