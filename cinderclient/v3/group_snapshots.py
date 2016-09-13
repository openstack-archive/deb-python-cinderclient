# Copyright (C) 2016 EMC Corporation.
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

"""group snapshot interface (v3)."""

import six
from six.moves.urllib.parse import urlencode

from cinderclient import base
from cinderclient.openstack.common.apiclient import base as common_base


class GroupSnapshot(base.Resource):
    """A group snapshot is a snapshot of a group."""
    def __repr__(self):
        return "<group_snapshot: %s>" % self.id

    def delete(self):
        """Delete this group snapshot."""
        return self.manager.delete(self)

    def update(self, **kwargs):
        """Update the name or description for this group snapshot."""
        return self.manager.update(self, **kwargs)


class GroupSnapshotManager(base.ManagerWithFind):
    """Manage :class:`GroupSnapshot` resources."""
    resource_class = GroupSnapshot

    def create(self, group_id, name=None, description=None,
               user_id=None,
               project_id=None):
        """Creates a group snapshot.

        :param group_id: Name or uuid of a group
        :param name: Name of the group snapshot
        :param description: Description of the group snapshot
        :param user_id: User id derived from context
        :param project_id: Project id derived from context
        :rtype: :class:`GroupSnapshot`
       """

        body = {
            'group_snapshot': {
                'group_id': group_id,
                'name': name,
                'description': description,
                'user_id': user_id,
                'project_id': project_id,
                'status': "creating",
            }
        }

        return self._create('/group_snapshots', body, 'group_snapshot')

    def get(self, group_snapshot_id):
        """Get a group snapshot.

        :param group_snapshot_id: The ID of the group snapshot to get.
        :rtype: :class:`GroupSnapshot`
        """
        return self._get("/group_snapshots/%s" % group_snapshot_id,
                         "group_snapshot")

    def list(self, detailed=True, search_opts=None):
        """Lists all group snapshots.

        :param detailed: list detailed info or not
        :param search_opts: search options
        :rtype: list of :class:`GroupSnapshot`
        """
        if search_opts is None:
            search_opts = {}

        qparams = {}

        for opt, val in six.iteritems(search_opts):
            if val:
                qparams[opt] = val

        query_string = "?%s" % urlencode(qparams) if qparams else ""

        detail = ""
        if detailed:
            detail = "/detail"

        return self._list("/group_snapshots%s%s" % (detail, query_string),
                          "group_snapshots")

    def delete(self, group_snapshot):
        """Delete a group_snapshot.

        :param group_snapshot: The :class:`GroupSnapshot` to delete.
        """
        return self._delete("/group_snapshots/%s" % base.getid(group_snapshot))

    def update(self, group_snapshot, **kwargs):
        """Update the name or description for a group_snapshot.

        :param group_snapshot: The :class:`GroupSnapshot` to update.
        """
        if not kwargs:
            return

        body = {"group_snapshot": kwargs}

        return self._update("/group_snapshots/%s" % base.getid(group_snapshot),
                            body)

    def _action(self, action, group_snapshot, info=None, **kwargs):
        """Perform a group_snapshot action."""
        body = {action: info}
        self.run_hooks('modify_body_for_action', body, **kwargs)
        url = '/group_snapshots/%s/action' % base.getid(group_snapshot)
        resp, body = self.api.client.post(url, body=body)
        return common_base.TupleWithMeta((resp, body), resp)
