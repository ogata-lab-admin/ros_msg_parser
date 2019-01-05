#!/usr/bin/env python
import unittest

import msg_parser

class TestActionParser(unittest.TestCase):

    def setUp(self):
        p = msg_parser.Parser()

        s = '''# Test Parser Action Data

# This is goal comment
float32 foo # Foo Comment
int32 goo # Hoge Comment
---
# This is result comment
bool success # Return Value
string message # Return Message
---
# This is feedback comment
bool status # Status Value
string message # Status Message
'''
        self._m = p.parse_action_str('test_pkg/hogeType', s)

    def test_comment(self):
        m = self._m
        self.assertEqual(m.comment, "Test Parser Action Data")

    def test_returnvalue_comment(self):
        m = self._m
        self.assertEqual(m.result.comment, 'This is result comment')

    def test_value_comment(self):
        m = self._m
        f = m.goal.members.findByName('foo')
        self.assertEqual(f.comment, 'Foo Comment')
        
    def test_foo(self):
        m = self._m
        f = m.goal.members.findByName('foo')
        self.assertIsNotNone(f)
        self.assertEqual(str(f.type), 'float32')

    def test_goo(self):
        m = self._m
        g = m.goal.members.findByName('goo')
        self.assertIsNotNone(g)
        self.assertEqual(str(g.type), 'int32')

    def test_hoo(self):
        m = self._m
        h = m.goal.members.findByName('hoo')
        self.assertIsNone(h)

    def test_result_comment(self):
        m = self._m
        self.assertEqual(m.result.comment, 'This is result comment')

    def test_feedbaxk_comment(self):
        m = self._m
        self.assertEqual(m.feedback.comment, 'This is feedback comment')

    def test_packageName(self):
        m = self._m
        self.assertEqual(m.packageName, 'test_pkg')

    def test_name(self):
        m = self._m
        self.assertEqual(m.name, 'hogeType')

    def test_resulst_value(self):
        m = self._m
        r = m.result.members.findByName('success')
        self.assertEqual(r.type.name, 'bool')
        self.assertEqual(r.comment, 'Return Value')

if __name__ == '__main__':
    uniittest.main()
