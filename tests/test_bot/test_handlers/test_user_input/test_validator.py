import unittest

from handlers.user_input import validator


class InputValidatorTestCase(unittest.TestCase):
    def test_is_valid_phone_number(self):
        self.assertTrue(validator.is_valid_phone_number('78901234567'))

        self.assertFalse(validator.is_valid_phone_number('789012345678'))
        self.assertFalse(validator.is_valid_phone_number('  +7 (890) 123 45-67.  '))
        self.assertFalse(validator.is_valid_phone_number('+88901234567'))
        self.assertFalse(validator.is_valid_phone_number('88901234567'))


if __name__ == '__main__':
    unittest.main()
