from typing import Dict

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from tele2client import event
from tele2client.client import Tele2Client

from bot.handlers.user_input import converter, validator
from bot.view import static


class BotStates(StatesGroup):
    input_phone_number = State()
    input_sms_code = State()
    cancel = State()


class Handler(object):
    _dispatcher: Dispatcher
    _users_data: Dict

    def __init__(self, dispatcher: Dispatcher):
        self._dispatcher = dispatcher
        self._users_data = {}

    def init(self):
        self._dispatcher.register_message_handler(self._start, commands=['start'])
        self._dispatcher.register_message_handler(
            self._input_phone_number,
            state=BotStates.input_phone_number,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_message_handler(
            self._input_sms_code,
            state=BotStates.input_sms_code,
            content_types=types.ContentTypes.TEXT
        )

    @staticmethod
    async def _start(message: types.Message):
        await message.answer(static.INPUT_PHONE_NUMBER)
        await BotStates.input_phone_number.set()

    async def _input_phone_number(self, message: types.Message, state: FSMContext):
        phone_number = converter.convert_format_phone_number(message.text)
        if not validator.is_valid_phone_number(phone_number):
            await message.answer(f'{static.FAILED_INPUT}. {static.INPUT_PHONE_NUMBER}.')

        await self._auth(message, state, phone_number)

    async def _input_sms_code(self, message: types.Message):
        user_data = self._get_user_data(self._get_user_hash(message))
        sms_waiter = user_data.get('sms_waiter')
        if sms_waiter is None:
            return

        sms_waiter: event.ValueWaiter
        sms_waiter.set(message.text)

    async def _get_sms_code(self, message: types.Message) -> str:
        await message.answer(static.INPUT_SMS_CODE)
        user_data = self._get_user_data(self._get_user_hash(message))
        sms_waiter = user_data['sms_waiter']

        sms_waiter: event.ValueWaiter
        return await sms_waiter.wait()

    async def _auth(self, message: types.Message, state: FSMContext, phone_number: str):
        sms_waiter = event.ValueWaiter()
        self._update_users_data(self._get_user_hash(message), sms_waiter=sms_waiter)

        client = Tele2Client(phone_number)
        await BotStates.input_sms_code.set()

        async def get_sms_code():
            return await self._get_sms_code(message)

        if not await client.auth(get_sms_code):
            await message.answer(static.FAILED_AUTHORIZATION)

        await message.answer(f'{static.REMAINS}')

        await state.finish()

    @staticmethod
    def _get_user_hash(message: types.Message) -> str:
        return f'{message.chat.id}_{message.from_user.id}'

    def _update_users_data(self, user_hash: str, **kwargs):
        user_data = self._users_data.get(user_hash, {})
        user_data.update(kwargs)
        self._users_data[user_hash] = user_data

    def _get_user_data(self, user_hash: str) -> Dict:
        return self._users_data.get(user_hash, {})
