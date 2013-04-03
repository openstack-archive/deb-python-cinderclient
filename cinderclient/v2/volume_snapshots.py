# Copyright 2013 OpenStack LLC.
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

"""Volume snapshot interface (1.1 extension)."""

import urllib

from cinderclient import base


class Snapshot(base.Resource):
    """A Snapshot is a point-in-time snapshot of an openstack volume."""
    def __repr__(self):
        return "<Snapshot: %s>" % self.id

    def delete(self):
        """Delete this snapshot."""
        self.manager.delete(self)

    def update(self, **kwargs):
        """Update the name or description for this snapshot."""
        self.manager.update(self, **kwargs)

    @property
    def progress(self):
        return self._info.get('os-extended-snapshot-attributes:progress')

    @property
    def project_id(self):
        return self._info.get('os-extended-snapshot-attributes:project_id')


class SnapshotManager(base.ManagerWithFind):
    """Manage :class:`Snapshot` resources."""
    resource_class = Snapshot

    def create(self, volume_id, force=False,
               name=None, description=None):

        """Create a snapshot of the given volume.

        :param volume_id: The ID of the volume to snapshot.
        :param force: If force is True, create a snapshot even if the volume is
        attached to an instance. Default is False.
        :param name: Name of the snapshot
        :param description: Description of the snapshot
        :rtype: :class:`Snapshot`
        """
        body = {'snapshot': {'volume_id': volume_id,
                             'force': force,
                             'name': name,
                             'description': description}}
        return self._create('/snapshots', body, 'snapshot')

    def get(self, snapshot_id):
        """Get a snapshot.

        :param snapshot_id: The ID of the snapshot to get.
        :rtype: :class:`Snapshot`
        """
        return self._get("/snapshots/%s" % snapshot_id, "snapshot")

    def list(self, detailed=True, search_opts=None):
        """Get a list of all snapshots.

        :rtype: list of :class:`Snapshot`
        """

        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in search_opts.iteritems():
            if val:
                qparams[opt] = val

        query_string = "?%s" % urllib.urlencode(qparams) if qparams else ""

        detail = ""
        if detailed:
            detail = "/detail"

        return self._list("/snapshots%s%s" % (detail, query_string),
                          "snapshots")

    def delete(self, snapshot):
        """Delete a snapshot.

        :param snapshot: The :class:`Snapshot` to delete.
        """
        self._delete("/snapshots/%s" % base.getid(snapshot))

    def update(self, snapshot, **kwargs):
        """Update the name or description for a snapshot.

        :param snapshot: The :class:`Snapshot` to delete.
        """
        if not kwargs:
            return

        body = {"snapshot": kwargs}

        self._update("/snapshots/%s" % base.getid(snapshot), body)
