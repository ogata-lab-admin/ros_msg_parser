#!/usr/bin/env python
import unittest

import msg_parser

class ROSMemberMock(object):
    def __init__(self):
        self.fee = 0
        self.bee = 0.0

    _full_text = '''# Test Parser Member Data
float32 fee # Fee comment
int32   bee # Bee comment'''
    _type = 'test_pkg_msgs/ROSMemberMock'

class ROSMember2Mock(object):
    def __init__(self):
        self.tee = 0
        self.dee = 0.0

    _full_text = '''# Test Parser Member Data 2
float32 tee # Fee comment
int32   dee # Bee comment'''
    _type = 'test_pkg_msgs/ROSMember2Mock'

class ROSSrvMock(object):
    def __init__(self):
        pass

    _request_class = ROSMemberMock
    _response_class = ROSMember2Mock

class ROSMsgMock(object):
    def __init__(self):
        self.foo = 0.0
        self.goo = 0
        self.hoge = ROSMemberMock()
    _full_text = '''# Test Parser Msg Data
float32 foo # Foo Comment
int32 goo # Goo Comment
test_pkg_msgs/ROSMemberMock hoge # Hoge Comment
================================================================================
MSG: test_pkg_msgs/ROSMemberMock
# Test Parser Member Data
float32 fee # Fee comment
int32   bee # Bee comment'''
    _type = 'test_pkg/ROSMsgMock'

class ROSDeepMsgMock(object):
    def __init__(self):
        self.a = 0.0
        self.b = 0
        self.c = ROSMsgMock()
    _full_text = '''
# Test Deep ROS Msg Data
float32 a # member a
int64 b # member b
test_pkg/ROSMsgMock c # Deep Data
================================================================================
MSG: test_pkg/ROSMsgMock
# Test Parser Msg Data
float32 foo # Foo Comment
int32 goo # Goo Comment
test_pkg_msgs/ROSMemberMock hoge # Hoge Comment
================================================================================
MSG: test_pkg_msgs/ROSMemberMock
# Test Parser Member Data
float32 fee # Fee comment
int32   bee # Bee comment'''
    _type = 'test_pkg/ROSMsgMock'

class TestParser(unittest.TestCase):

    def setUp(self):
        p = msg_parser.Parser()

        self._m = p.parse_msg_class(ROSMsgMock)
        self._d = p.parse_msg_class(ROSDeepMsgMock)

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
        self.assertEqual(m.name, 'ROSMsgMock')

    def test_hoge(self):
        m = self._m
        h = m.members.findByName('hoge')
        self.assertEqual(h.type.fullName, 'test_pkg_msgs/ROSMemberMock')

        f = h.type.members.findByName('fee')
        self.assertIsNotNone(f)

    def test_deep_a(self):
        m = self._d
        a = m.members.findByName('a')
        self.assertIsNotNone(a)
        self.assertEqual(a.type.fullName, 'float32')

    def test_deep_c(self):
        m = self._d
        c = m.members.findByName('c')
        self.assertIsNotNone(c)
        self.assertEqual(c.type.fullName, 'test_pkg/ROSMsgMock')

        foo = c.type.members.findByName('foo')
        self.assertIsNotNone(foo)
        self.assertEqual(foo.type.fullName, 'float32')

        hoge = c.type.members.findByName('hoge')
        self.assertIsNotNone(hoge)

        fee = hoge.type.members.findByName('fee')
        self.assertIsNotNone(fee)
        self.assertEqual(fee.type.fullName, 'float32')
        
if __name__ == '__main__':
    uniittest.main()
