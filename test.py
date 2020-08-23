import unittest
import tempfile
import parser2

class TestParseKey(unittest.TestCase):

    def testRegularString(self):
        s = r'"bloop"'
        self.reader = parser2.CharReader(s)
        self.reader.next()
        self.assertEqual('bloop', parser2.parse_key(self.reader))

    def testEscapeCharDoubleQuote(self):
        s = r'"\"bloop\"\na\/b\\c\na\b\f\r\t"'
        self.reader = parser2.CharReader(s)
        self.reader.next()
        
        ans = r'\"bloop\"\na\/b\\c\na\b\f\r\t'
        res = parser2.parse_key(self.reader)

        self.assertEqual(ans, res)


if __name__ == '__main__':
    unittest.main()
