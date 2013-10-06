# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from cinderclient.tests import utils
from cinderclient.tests.v1 import fakes


cs = fakes.FakeClient()


class SnapshotActionsTest(utils.TestCase):
    def test_update_snapshot_status(self):
        s = cs.volume_snapshots.get('1234')
        cs.volume_snapshots.update_snapshot_status(s,
                                                   {'status': 'available'})
        cs.assert_called('POST', '/snapshots/1234/action')

    def test_update_snapshot_status_with_progress(self):
        s = cs.volume_snapshots.get('1234')
        cs.volume_snapshots.update_snapshot_status(s,
                                                   {'status': 'available',
                                                    'progress': '73%'})
        cs.assert_called('POST', '/snapshots/1234/action')
