from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AccessMiddleware(BaseMiddleware):
    """Не пропускает сообщения от ботов"""
    @staticmethod
    async def on_process_message(message: types.Message, _):
        if message.from_user.is_bot:
            await message.answer('Access Denied')
            raise CancelHandler()
