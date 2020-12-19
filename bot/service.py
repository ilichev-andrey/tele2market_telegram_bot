from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.middlewares import AccessMiddleware
from handlers import handler


class Service(object):
    def __init__(self, api_token: str):
        self.dispatcher = Dispatcher(Bot(token=api_token), storage=MemoryStorage())
        self.dispatcher.middleware.setup(AccessMiddleware())
        self.handler = handler.Handler(self.dispatcher)

    def init(self):
        self.handler.init()

    def run(self):
        executor.start_polling(self.dispatcher, skip_updates=False)
