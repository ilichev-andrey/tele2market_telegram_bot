import unittest

from handlers.user_input import converter


class InputConverterTestCase(unittest.TestCase):
    def test_convert_format_phone_number(self):
        self.assertEqual('78901234567', converter.convert_format_phone_number('  +7 (890) 123 45-67.  '))
        self.assertEqual('78901234567', converter.convert_format_phone_number('+88901234567'))
        self.assertEqual('78901234567', converter.convert_format_phone_number('88901234567'))


if __name__ == '__main__':
    unittest.main()
