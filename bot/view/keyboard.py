from typing import Tuple

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def create_reply_keyboard_markup(button_names: Tuple) -> ReplyKeyboardMarkup:
    poll_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button_name in button_names:
        poll_keyboard.add(KeyboardButton(text=button_name))

    return poll_keyboard
