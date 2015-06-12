# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import sys

import mock
from six import moves

from cinderclient import exceptions
from cinderclient import utils
from cinderclient import base
from cinderclient.tests.unit import utils as test_utils

UUID = '8e8ec658-c7b0-4243-bdf8-6f7f2952c0d0'


class FakeResource(object):
    NAME_ATTR = 'name'

    def __init__(self, _id, properties):
        self.id = _id
        try:
            self.name = properties['name']
        except KeyError:
            pass


class FakeManager(base.ManagerWithFind):

    resource_class = FakeResource

    resources = [
        FakeResource('1234', {'name': 'entity_one'}),
        FakeResource(UUID, {'name': 'entity_two'}),
        FakeResource('5678', {'name': '9876'})
    ]

    def get(self, resource_id):
        for resource in self.resources:
            if resource.id == str(resource_id):
                return resource
        raise exceptions.NotFound(resource_id)

    def list(self, search_opts):
        return self.resources


class FakeDisplayResource(object):
    NAME_ATTR = 'display_name'

    def __init__(self, _id, properties):
        self.id = _id
        try:
            self.display_name = properties['display_name']
        except KeyError:
            pass


class FakeDisplayManager(FakeManager):

    resource_class = FakeDisplayResource

    resources = [
        FakeDisplayResource('4242', {'display_name': 'entity_three'}),
    ]


class FindResourceTestCase(test_utils.TestCase):

    def setUp(self):
        super(FindResourceTestCase, self).setUp()
        self.manager = FakeManager(None)

    def test_find_none(self):
        self.manager.find = mock.Mock(side_effect=self.manager.find)
        self.assertRaises(exceptions.CommandError,
                          utils.find_resource,
                          self.manager,
                          'asdf')
        self.assertEqual(2, self.manager.find.call_count)

    def test_find_by_integer_id(self):
        output = utils.find_resource(self.manager, 1234)
        self.assertEqual(self.manager.get('1234'), output)

    def test_find_by_str_id(self):
        output = utils.find_resource(self.manager, '1234')
        self.assertEqual(self.manager.get('1234'), output)

    def test_find_by_uuid(self):
        output = utils.find_resource(self.manager, UUID)
        self.assertEqual(self.manager.get(UUID), output)

    def test_find_by_str_name(self):
        output = utils.find_resource(self.manager, 'entity_one')
        self.assertEqual(self.manager.get('1234'), output)

    def test_find_by_str_displayname(self):
        display_manager = FakeDisplayManager(None)
        output = utils.find_resource(display_manager, 'entity_three')
        self.assertEqual(display_manager.get('4242'), output)


class CaptureStdout(object):
    """Context manager for capturing stdout from statements in its block."""
    def __enter__(self):
        self.real_stdout = sys.stdout
        self.stringio = moves.StringIO()
        sys.stdout = self.stringio
        return self

    def __exit__(self, *args):
        sys.stdout = self.real_stdout
        self.stringio.seek(0)
        self.read = self.stringio.read


class PrintListTestCase(test_utils.TestCase):

    def test_print_list_with_list(self):
        Row = collections.namedtuple('Row', ['a', 'b'])
        to_print = [Row(a=3, b=4), Row(a=1, b=2)]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['a', 'b'])
        # Output should be sorted by the first key (a)
        self.assertEqual("""\
+---+---+
| a | b |
+---+---+
| 1 | 2 |
| 3 | 4 |
+---+---+
""", cso.read())

    def test_print_list_with_None_data(self):
        Row = collections.namedtuple('Row', ['a', 'b'])
        to_print = [Row(a=3, b=None), Row(a=1, b=2)]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['a', 'b'])
        # Output should be sorted by the first key (a)
        self.assertEqual("""\
+---+---+
| a | b |
+---+---+
| 1 | 2 |
| 3 | - |
+---+---+
""", cso.read())

    def test_print_list_with_list_sortby(self):
        Row = collections.namedtuple('Row', ['a', 'b'])
        to_print = [Row(a=4, b=3), Row(a=2, b=1)]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['a', 'b'], sortby_index=1)
        # Output should be sorted by the second key (b)
        self.assertEqual("""\
+---+---+
| a | b |
+---+---+
| 2 | 1 |
| 4 | 3 |
+---+---+
""", cso.read())

    def test_print_list_with_list_no_sort(self):
        Row = collections.namedtuple('Row', ['a', 'b'])
        to_print = [Row(a=3, b=4), Row(a=1, b=2)]
        with CaptureStdout() as cso:
            utils.print_list(to_print, ['a', 'b'], sortby_index=None)
        # Output should be in the order given
        self.assertEqual("""\
+---+---+
| a | b |
+---+---+
| 3 | 4 |
| 1 | 2 |
+---+---+
""", cso.read())

    def test_print_list_with_generator(self):
        Row = collections.namedtuple('Row', ['a', 'b'])

        def gen_rows():
            for row in [Row(a=1, b=2), Row(a=3, b=4)]:
                yield row
        with CaptureStdout() as cso:
            utils.print_list(gen_rows(), ['a', 'b'])
        self.assertEqual("""\
+---+---+
| a | b |
+---+---+
| 1 | 2 |
| 3 | 4 |
+---+---+
""", cso.read())
