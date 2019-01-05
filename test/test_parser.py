#!/usr/bin/env python
import unittest

import msg_parser

class TestParser(unittest.TestCase):

    def setUp(self):
        p = msg_parser.Parser()

        s = '''# Test Parser Msg Data
float32 foo # Foo Comment
int32 goo # Hoge Comment
uint32 a = 1 # the first data
uint32 b = 2 # the second data
uint32 c = 3 # the third data'''
        self._m = p.parse_msg_str('test_pkg/hogeType', s)

    def test_comment(self):
        m = self._m
        self.assertEqual(m.comment, "Test Parser Msg Data")

    def test_value_comment(self):
        m = self._m
        f = m.members.findByName('foo')
        self.assertEqual(f.comment, 'Foo Comment')
        
    def test_foo(self):
        m = self._m
        f = m.members.findByName('foo')
        self.assertIsNotNone(f)
        self.assertEqual(str(f.type), 'float32')

    def test_goo(self):
        m = self._m
        g = m.members.findByName('goo')
        self.assertIsNotNone(g)
        self.assertEqual(str(g.type), 'int32')

    def test_hoo(self):
        m = self._m
        h = m.members.findByName('hoo')
        self.assertIsNone(h)

    def test_packageName(self):
        m = self._m
        self.assertEqual(m.packageName, 'test_pkg')

    def test_name(self):
        m = self._m
        self.assertEqual(m.name, 'hogeType')

    def test_const_a(self):
        m = self._m
        a = m.members.findByName('a')
        self.assertEqual(a.type.fullName, 'uint32')
        self.assertEqual(a.value_str, '1')
        self.assertEqual(a.value, 1)

if __name__ == '__main__':
    uniittest.main()
