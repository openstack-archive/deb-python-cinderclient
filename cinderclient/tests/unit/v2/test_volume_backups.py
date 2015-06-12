# Copyright (C) 2013 Hewlett-Packard Development Company, L.P.
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

from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v2 import fakes


cs = fakes.FakeClient()


class VolumeBackupsTest(utils.TestCase):

    def test_create(self):
        cs.backups.create('2b695faf-b963-40c8-8464-274008fbcef4')
        cs.assert_called('POST', '/backups')

    def test_create_full(self):
        cs.backups.create('2b695faf-b963-40c8-8464-274008fbcef4',
                          None, None, False)
        cs.assert_called('POST', '/backups')

    def test_create_incremental(self):
        cs.backups.create('2b695faf-b963-40c8-8464-274008fbcef4',
                          None, None, True)
        cs.assert_called('POST', '/backups')

    def test_get(self):
        backup_id = '76a17945-3c6f-435c-975b-b5685db10b62'
        cs.backups.get(backup_id)
        cs.assert_called('GET', '/backups/%s' % backup_id)

    def test_list(self):
        cs.backups.list()
        cs.assert_called('GET', '/backups/detail')

    def test_delete(self):
        b = cs.backups.list()[0]
        b.delete()
        cs.assert_called('DELETE',
                         '/backups/76a17945-3c6f-435c-975b-b5685db10b62')
        cs.backups.delete('76a17945-3c6f-435c-975b-b5685db10b62')
        cs.assert_called('DELETE',
                         '/backups/76a17945-3c6f-435c-975b-b5685db10b62')
        cs.backups.delete(b)
        cs.assert_called('DELETE',
                         '/backups/76a17945-3c6f-435c-975b-b5685db10b62')

    def test_restore(self):
        backup_id = '76a17945-3c6f-435c-975b-b5685db10b62'
        cs.restores.restore(backup_id)
        cs.assert_called('POST', '/backups/%s/restore' % backup_id)

    def test_record_export(self):
        backup_id = '76a17945-3c6f-435c-975b-b5685db10b62'
        cs.backups.export_record(backup_id)
        cs.assert_called('GET',
                         '/backups/%s/export_record' % backup_id)

    def test_record_import(self):
        backup_service = 'fake-backup-service'
        backup_url = 'fake-backup-url'
        expected_body = {'backup-record': {'backup_service': backup_service,
                                           'backup_url': backup_url}}
        cs.backups.import_record(backup_service, backup_url)
        cs.assert_called('POST', '/backups/import_record', expected_body)
