import re


def is_valid_phone_number(phone_number: str) -> bool:
    return re.fullmatch(r'7\d{10}', phone_number) is not None


def is_valid_number(number: str) -> bool:
    return number.isdigit()
