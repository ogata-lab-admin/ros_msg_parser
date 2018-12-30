
#!/usr/bin/env python
import unittest

import msg_parser

class TestException(unittest.TestCase):

    def test_invalid_primitive(self):
        p = msg_parser.Parser()
        s = '''

float foo '''
        with self.assertRaises(msg_parser.InvalidPrimitiveTypeName) as cm:
            p.parse_str('test_pkg/hogeType', s)

        the_exception = cm.exception
        self.assertEqual(the_exception._i, 2)
        


if __name__ == '__main__':
    uniittest.main()
