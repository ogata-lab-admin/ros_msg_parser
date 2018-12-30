#!/usr/bin/env python
import unittest

import msg_parser

class TestParser(unittest.TestCase):

    def setUp(self):
        p = msg_parser.Parser()

        s = '''
float foo
int32 goo '''
        self._m = p.parse_str('test_pkg/hogeType', s)

    
    def test_foo(self):
        m = self._m
        f = m.members.findByName('foo')
        self.assertIsNotNone(f)
        self.assertEqual(str(f.type), 'float')

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
