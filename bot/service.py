from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.handlers import handler
from bot.middlewares import AccessMiddleware
from executor.task_manager import TaskQueue


class Service(object):
    _dispatcher: Dispatcher
    _handler: handler.Handler
    _task_queue: TaskQueue

    def __init__(self, api_token: str, task_queue: TaskQueue):
        self._dispatcher = Dispatcher(Bot(token=api_token), storage=MemoryStorage())
        self._dispatcher.middleware.setup(AccessMiddleware())
        self._task_queue = task_queue
        self._handler = handler.Handler(self._dispatcher, self._task_queue)

    def init(self):
        self._handler.init()

    def run(self):
        executor.start_polling(self._dispatcher, skip_updates=False)
