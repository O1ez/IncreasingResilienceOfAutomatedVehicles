import unittest
import parser
import pyparsing as pp
from functools import partial
class TestCalculations(unittest.TestCase):

    def test_and(self):
        parsed_list = parser.parse_line("x and y and z")
        self.assertEqual(parsed_list, [["x", "and", "y"], "and", "z"])

    def test_or(self):
        parsed_list = parser.parse_line("x or y or z")
        self.assertEqual(parsed_list, [["x", "or", "y"], "or", "z"])

    def test_and_or(self):
        parsed_list = parser.parse_line("a and b or c and d")
        self.assertEqual(parsed_list, [["a", "and", "b"], "or", ["c", "and", "d"]])

    def test_not(self):
        parsed_list = parser.parse_line("a and b or not c and not d")
        self.assertEqual(parsed_list, [["a", "and", "b"], "or", [["not", "c"], "and", ["not", "d"]]])

    def test_parantheses(self):
        parsed_list = parser.parse_line("(a or b) and c")
        self.assertEqual(parsed_list, [["a", "or", "b"], "and", "c"])

    def test_variables(self):
        self.assertRaises(pp.exceptions.ParseException, partial(parser.parse_line, "!"))
        
        parsed_list = parser.parse_line("X1")
        self.assertEqual(parsed_list, "X1")

        parsed_list = parser.parse_line("1")
        self.assertEqual(parsed_list, "1")

        parsed_list = parser.parse_line("1X")
        self.assertEqual(parsed_list, "1X")

if __name__ == '__main__':
    unittest.main()