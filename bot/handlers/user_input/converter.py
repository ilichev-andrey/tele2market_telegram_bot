import re


def convert_format_phone_number(phone_number: str) -> str:
    phone_number = re.sub(r'[^\d]', '', phone_number)
    return '7{}'.format(phone_number[1:])
