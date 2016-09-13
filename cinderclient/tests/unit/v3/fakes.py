# Copyright (c) 2013 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime

from cinderclient.tests.unit import fakes
from cinderclient.v3 import client
from cinderclient.tests.unit.v2 import fakes as fake_v2


def _stub_group(detailed=True, **kwargs):
    group = {
        "name": "test-1",
        "id": "1234",
    }
    if detailed:
        details = {
            "created_at": "2012-08-28T16:30:31.000000",
            "description": "test-1-desc",
            "availability_zone": "zone1",
            "status": "available",
            "group_type": "my_group_type",
        }
        group.update(details)
    group.update(kwargs)
    return group


def _stub_group_snapshot(detailed=True, **kwargs):
    group_snapshot = {
        "name": None,
        "id": "5678",
    }
    if detailed:
        details = {
            "created_at": "2012-08-28T16:30:31.000000",
            "description": None,
            "name": None,
            "id": "5678",
            "status": "available",
            "group_id": "1234",
        }
        group_snapshot.update(details)
    group_snapshot.update(kwargs)
    return group_snapshot


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, api_version=None, *args, **kwargs):
        client.Client.__init__(self, 'username', 'password',
                               'project_id', 'auth_url',
                               extensions=kwargs.get('extensions'))
        self.api_version = api_version
        self.client = FakeHTTPClient(api_version=api_version,
                                     **kwargs)

    def get_volume_api_version_from_endpoint(self):
        return self.client.get_volume_api_version_from_endpoint()


class FakeHTTPClient(fake_v2.FakeHTTPClient):

    def __init__(self, **kwargs):
        super(FakeHTTPClient, self).__init__()
        self.management_url = 'http://10.0.2.15:8776/v3/fake'
        vars(self).update(kwargs)

    #
    # Services
    #
    def get_os_services(self, **kw):
        host = kw.get('host', None)
        binary = kw.get('binary', None)
        services = [
            {
                'id': 1,
                'binary': 'cinder-volume',
                'host': 'host1',
                'zone': 'cinder',
                'status': 'enabled',
                'state': 'up',
                'updated_at': datetime(2012, 10, 29, 13, 42, 2),
                'cluster': 'cluster1',
            },
            {
                'id': 2,
                'binary': 'cinder-volume',
                'host': 'host2',
                'zone': 'cinder',
                'status': 'disabled',
                'state': 'down',
                'updated_at': datetime(2012, 9, 18, 8, 3, 38),
                'cluster': 'cluster1',
            },
            {
                'id': 3,
                'binary': 'cinder-scheduler',
                'host': 'host2',
                'zone': 'cinder',
                'status': 'disabled',
                'state': 'down',
                'updated_at': datetime(2012, 9, 18, 8, 3, 38),
                'cluster': 'cluster2',
            },
        ]
        if host:
            services = list(filter(lambda i: i['host'] == host, services))
        if binary:
            services = list(filter(lambda i: i['binary'] == binary, services))
        if not self.api_version.matches('3.7'):
            for svc in services:
                del svc['cluster']
        return (200, {}, {'services': services})

    #
    # Clusters
    #
    def _filter_clusters(self, return_keys, **kw):
        date = datetime(2012, 10, 29, 13, 42, 2),
        clusters = [
            {
                'id': '1',
                'name': 'cluster1@lvmdriver-1',
                'state': 'up',
                'status': 'enabled',
                'binary': 'cinder-volume',
                'is_up': 'True',
                'disabled': 'False',
                'disabled_reason': None,
                'num_hosts': '3',
                'num_down_hosts': '2',
                'updated_at': date,
                'created_at': date,
                'last_heartbeat': date,
            },
            {
                'id': '2',
                'name': 'cluster1@lvmdriver-2',
                'state': 'down',
                'status': 'enabled',
                'binary': 'cinder-volume',
                'is_up': 'False',
                'disabled': 'False',
                'disabled_reason': None,
                'num_hosts': '2',
                'num_down_hosts': '2',
                'updated_at': date,
                'created_at': date,
                'last_heartbeat': date,
            },
            {
                'id': '3',
                'name': 'cluster2',
                'state': 'up',
                'status': 'disabled',
                'binary': 'cinder-backup',
                'is_up': 'True',
                'disabled': 'True',
                'disabled_reason': 'Reason',
                'num_hosts': '1',
                'num_down_hosts': '0',
                'updated_at': date,
                'created_at': date,
                'last_heartbeat': date,
            },
        ]

        for key, value in kw.items():
            clusters = [cluster for cluster in clusters
                        if cluster[key] == str(value)]

        result = []
        for cluster in clusters:
            result.append({key: cluster[key] for key in return_keys})
        return result

    CLUSTER_SUMMARY_KEYS = ('name', 'binary', 'state', 'status')
    CLUSTER_DETAIL_KEYS = (CLUSTER_SUMMARY_KEYS +
                           ('num_hosts', 'num_down_hosts', 'last_heartbeat',
                            'disabled_reason', 'created_at', 'updated_at'))

    def get_clusters(self, **kw):
        clusters = self._filter_clusters(self.CLUSTER_SUMMARY_KEYS, **kw)
        return (200, {}, {'clusters': clusters})

    def get_clusters_detail(self, **kw):
        clusters = self._filter_clusters(self.CLUSTER_DETAIL_KEYS, **kw)
        return (200, {}, {'clusters': clusters})

    def get_clusters_1(self):
        res = self.get_clusters_detail(id=1)
        return (200, {}, {'cluster': res[2]['clusters'][0]})

    def put_clusters_enable(self, body):
        res = self.get_clusters(id=1)
        return (200, {}, {'cluster': res[2]['clusters'][0]})

    def put_clusters_disable(self, body):
        res = self.get_clusters(id=3)
        return (200, {}, {'cluster': res[2]['clusters'][0]})

    #
    # Backups
    #
    def put_backups_1234(self, **kw):
        backup = fake_v2._stub_backup(
            id='1234',
            base_uri='http://localhost:8776',
            tenant_id='0fa851f6668144cf9cd8c8419c1646c1')
        return (200, {},
                {'backups': backup})

    #
    # GroupTypes
    #
    def get_group_types(self, **kw):
        return (200, {}, {
            'group_types': [{'id': 1,
                             'name': 'test-type-1',
                             'description': 'test_type-1-desc',
                             'group_specs': {}},
                            {'id': 2,
                             'name': 'test-type-2',
                             'description': 'test_type-2-desc',
                             'group_specs': {}}]})

    def get_group_types_1(self, **kw):
        return (200, {}, {'group_type': {'id': 1,
                          'name': 'test-type-1',
                          'description': 'test_type-1-desc',
                          'group_specs': {u'key': u'value'}}})

    def get_group_types_2(self, **kw):
        return (200, {}, {'group_type': {'id': 2,
                          'name': 'test-type-2',
                          'description': 'test_type-2-desc',
                          'group_specs': {}}})

    def get_group_types_3(self, **kw):
        return (200, {}, {'group_type': {'id': 3,
                          'name': 'test-type-3',
                          'description': 'test_type-3-desc',
                          'group_specs': {},
                          'is_public': False}})

    def get_group_types_default(self, **kw):
        return self.get_group_types_1()

    def post_group_types(self, body, **kw):
        return (202, {}, {'group_type': {'id': 3,
                          'name': 'test-type-3',
                          'description': 'test_type-3-desc',
                          'group_specs': {}}})

    def post_group_types_1_group_specs(self, body, **kw):
        assert list(body) == ['group_specs']
        return (200, {}, {'group_specs': {'k': 'v'}})

    def delete_group_types_1_group_specs_k(self, **kw):
        return(204, {}, None)

    def delete_group_types_1_group_specs_m(self, **kw):
        return(204, {}, None)

    def delete_group_types_1(self, **kw):
        return (202, {}, None)

    def delete_group_types_3_group_specs_k(self, **kw):
        return(204, {}, None)

    def delete_group_types_3(self, **kw):
        return (202, {}, None)

    def put_group_types_1(self, **kw):
        return self.get_group_types_1()

    #
    # Groups
    #
    def get_groups_detail(self, **kw):
        return (200, {}, {"groups": [
            _stub_group(id='1234'),
            _stub_group(id='4567')]})

    def get_groups(self, **kw):
        return (200, {}, {"groups": [
            _stub_group(detailed=False, id='1234'),
            _stub_group(detailed=False, id='4567')]})

    def get_groups_1234(self, **kw):
        return (200, {}, {'group':
                          _stub_group(id='1234')})

    def post_groups(self, **kw):
        group = _stub_group(id='1234', group_type='my_group_type',
                            volume_types=['type1', 'type2'])
        return (202, {}, {'group': group})

    def put_groups_1234(self, **kw):
        return (200, {}, {'group': {}})

    def post_groups_1234_action(self, body, **kw):
        resp = 202
        assert len(list(body)) == 1
        action = list(body)[0]
        if action == 'delete':
            assert 'delete-volumes' in body[action]
        else:
            raise AssertionError("Unexpected action: %s" % action)
        return (resp, {}, {})

    def post_groups_action(self, body, **kw):
        group = _stub_group(id='1234', group_type='my_group_type',
                            volume_types=['type1', 'type2'])
        resp = 202
        assert len(list(body)) == 1
        action = list(body)[0]
        if action == 'create-from-src':
            assert ('group_snapshot_id' in body[action] or
                    'source_group_id' in body[action])
        else:
            raise AssertionError("Unexpected action: %s" % action)
        return (resp, {}, {'group': group})

    #
    # group_snapshots
    #

    def get_group_snapshots_detail(self, **kw):
        return (200, {}, {"group_snapshots": [
            _stub_group_snapshot(id='1234'),
            _stub_group_snapshot(id='4567')]})

    def get_group_snapshots(self, **kw):
        return (200, {}, {"group_snapshots": [
            _stub_group_snapshot(detailed=False, id='1234'),
            _stub_group_snapshot(detailed=False, id='4567')]})

    def get_group_snapshots_1234(self, **kw):
        return (200, {}, {'group_snapshot': _stub_group_snapshot(id='1234')})

    def get_group_snapshots_5678(self, **kw):
        return (200, {}, {'group_snapshot': _stub_group_snapshot(id='5678')})

    def post_group_snapshots(self, **kw):
        group_snap = _stub_group_snapshot()
        return (202, {}, {'group_snapshot': group_snap})

    def put_group_snapshots_1234(self, **kw):
        return (200, {}, {'group_snapshot': {}})

    def delete_group_snapshots_1234(self, **kw):
        return (202, {}, {})

    #
    # Manageable volumes/snapshots
    #
    def get_manageable_volumes(self, **kw):
        vol_id = "volume-ffffffff-0000-ffff-0000-ffffffffffff"
        vols = [{"size": 4, "safe_to_manage": False, "actual_size": 4.0,
                 "reference": {"source-name": vol_id}},
                {"size": 5, "safe_to_manage": True, "actual_size": 4.3,
                 "reference": {"source-name": "myvol"}}]
        return (200, {}, {"manageable-volumes": vols})

    def get_manageable_volumes_detail(self, **kw):
        vol_id = "volume-ffffffff-0000-ffff-0000-ffffffffffff"
        vols = [{"size": 4, "reason_not_safe": "volume in use",
                 "safe_to_manage": False, "extra_info": "qos_setting:high",
                 "reference": {"source-name": vol_id},
                 "actual_size": 4.0},
                {"size": 5, "reason_not_safe": None, "safe_to_manage": True,
                 "extra_info": "qos_setting:low", "actual_size": 4.3,
                 "reference": {"source-name": "myvol"}}]
        return (200, {}, {"manageable-volumes": vols})

    def get_manageable_snapshots(self, **kw):
        snap_id = "snapshot-ffffffff-0000-ffff-0000-ffffffffffff"
        snaps = [{"actual_size": 4.0, "size": 4,
                 "safe_to_manage": False, "source_id_type": "source-name",
                 "source_cinder_id": "00000000-ffff-0000-ffff-00000000",
                 "reference": {"source-name": snap_id},
                 "source_identifier": "volume-00000000-ffff-0000-ffff-000000"},
                {"actual_size": 4.3, "reference": {"source-name": "mysnap"},
                 "source_id_type": "source-name", "source_identifier": "myvol",
                 "safe_to_manage": True, "source_cinder_id": None, "size": 5}]
        return (200, {}, {"manageable-snapshots": snaps})

    def get_manageable_snapshots_detail(self, **kw):
        snap_id = "snapshot-ffffffff-0000-ffff-0000-ffffffffffff"
        snaps = [{"actual_size": 4.0, "size": 4,
                 "safe_to_manage": False, "source_id_type": "source-name",
                 "source_cinder_id": "00000000-ffff-0000-ffff-00000000",
                 "reference": {"source-name": snap_id},
                 "source_identifier": "volume-00000000-ffff-0000-ffff-000000",
                 "extra_info": "qos_setting:high",
                 "reason_not_safe": "snapshot in use"},
                {"actual_size": 4.3, "reference": {"source-name": "mysnap"},
                 "safe_to_manage": True, "source_cinder_id": None,
                 "source_id_type": "source-name", "identifier": "mysnap",
                 "source_identifier": "myvol", "size": 5,
                 "extra_info": "qos_setting:low", "reason_not_safe": None}]
        return (200, {}, {"manageable-snapshots": snaps})

    #
    # Messages
    #
    def get_messages(self, **kw):
        return 200, {}, {'messages': [
            {
                'id': '1234',
                'event_id': 'VOLUME_000002',
                'user_message': 'Fake Message',
                'created_at': '2012-08-27T00:00:00.000000',
                'guaranteed_until': "2013-11-12T21:00:00.000000",
            },
            {
                'id': '12345',
                'event_id': 'VOLUME_000002',
                'user_message': 'Fake Message',
                'created_at': '2012-08-27T00:00:00.000000',
                'guaranteed_until': "2013-11-12T21:00:00.000000",
            }
        ]}

    def delete_messages_1234(self, **kw):
        return 204, {}, None

    def delete_messages_12345(self, **kw):
        return 204, {}, None

    def get_messages_1234(self, **kw):
        message = {
            'id': '1234',
            'event_id': 'VOLUME_000002',
            'user_message': 'Fake Message',
            'created_at': '2012-08-27T00:00:00.000000',
            'guaranteed_until': "2013-11-12T21:00:00.000000",
        }
        return 200, {}, {'message': message}

    def get_messages_12345(self, **kw):
        message = {
            'id': '12345',
            'event_id': 'VOLUME_000002',
            'user_message': 'Fake Message',
            'created_at': '2012-08-27T00:00:00.000000',
            'guaranteed_until': "2013-11-12T21:00:00.000000",
        }
        return 200, {}, {'message': message}
