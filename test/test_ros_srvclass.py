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
    _type = 'hoge_msg/ROSSrvMock'
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

        self._m = p.parse_srv_class(ROSSrvMock)

    def test_srv_class(self):
        m = self._m
        self.assertEqual(m.request.fullName, 'test_pkg_msgs/ROSMemberMock')
        self.assertEqual(m.response.fullName, 'test_pkg_msgs/ROSMember2Mock')
        
if __name__ == '__main__':
    uniittest.main()
