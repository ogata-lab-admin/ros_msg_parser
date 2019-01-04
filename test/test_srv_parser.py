#!/usr/bin/env python
import unittest

import msg_parser

class TestParser(unittest.TestCase):

    def setUp(self):
        p = msg_parser.Parser()

        s = '''# Test Parser Srv Data

# This is argument comment
float32 foo # Foo Comment
int32 goo # Hoge Comment
---
# This is return value comment
bool success # Return Value
string message # Return Message
'''
        self._m = p.parse_srv_str('test_pkg/hogeType', s)

    def test_comment(self):
        m = self._m
        self.assertEqual(m.comment, "Test Parser Srv Data")

    def test_returnvalue_comment(self):
        m = self._m
        self.assertEqual(m.arg.comment, 'This is argument comment')

    def test_value_comment(self):
        m = self._m
        f = m.arg.members.findByName('foo')
        self.assertEqual(f.comment, 'Foo Comment')
        
    def test_foo(self):
        m = self._m
        f = m.arg.members.findByName('foo')
        self.assertIsNotNone(f)
        self.assertEqual(str(f.type), 'float32')

    def test_goo(self):
        m = self._m
        g = m.arg.members.findByName('goo')
        self.assertIsNotNone(g)
        self.assertEqual(str(g.type), 'int32')

    def test_hoo(self):
        m = self._m
        h = m.arg.members.findByName('hoo')
        self.assertIsNone(h)

    def test_returnvalue_comment(self):
        m = self._m
        self.assertEqual(m.returns.comment, 'This is return value comment')
        
    def test_packageName(self):
        m = self._m
        self.assertEqual(m.packageName, 'test_pkg')

    def test_name(self):
        m = self._m
        self.assertEqual(m.name, 'hogeType')

    def test_return_value(self):
        m = self._m
        r = m.returns.members.findByName('success')
        self.assertEqual(r.type.name, 'bool')
        self.assertEqual(r.comment, 'Return Value')

if __name__ == '__main__':
    uniittest.main()
