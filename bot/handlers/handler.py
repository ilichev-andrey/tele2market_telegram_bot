from typing import Dict

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from tele2client import event, containers as tele2containers
from tele2client.client import Tele2Client

from bot import containers
from bot.handlers import input_remains
from bot.handlers.user_input import converter, validator
from bot.view import buttons, keyboard, static


class BotStates(StatesGroup):
    input_phone_number = State()
    input_sms_code = State()
    input_remains = State()


class Handler(object):
    _dispatcher: Dispatcher
    _users_data: Dict[str, containers.UserData]
    _input_remains: input_remains.InputRemainsHandler

    def __init__(self, dispatcher: Dispatcher):
        self._dispatcher = dispatcher
        self._users_data = {}
        self._input_remains = input_remains.InputRemainsHandler(dispatcher, self._on_input_remains)

    def init(self):
        self._input_remains.init(BotStates.input_remains)
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

    async def _input_phone_number(self, message: types.Message):
        phone_number = converter.convert_format_phone_number(message.text)
        if not validator.is_valid_phone_number(phone_number):
            await message.answer(f'{static.FAILED_INPUT}. {static.INPUT_PHONE_NUMBER}.')

        await self._auth(message, phone_number)

    async def _input_sms_code(self, message: types.Message):
        user_data = self._get_user_data(self._get_user_hash_by_message(message))
        sms_waiter = user_data.sms_waiter
        if sms_waiter is None:
            return

        sms_waiter.set(message.text)

    async def _get_sms_code(self, message: types.Message) -> str:
        await message.answer(static.INPUT_SMS_CODE)
        user_data = self._get_user_data(self._get_user_hash_by_message(message))
        return await user_data.sms_waiter.wait()

    async def _auth(self, message: types.Message, phone_number: str):
        user_hash = self._get_user_hash_by_message(message)
        sms_waiter = event.ValueWaiter()
        self._update_users_data(user_hash, sms_waiter=sms_waiter)

        client = Tele2Client(phone_number)
        self._update_users_data(user_hash, tele2client=client)
        await BotStates.input_sms_code.set()

        async def get_sms_code():
            return await self._get_sms_code(message)

        if not await client.auth(get_sms_code):
            await message.answer(static.FAILED_AUTHORIZATION)

        remain_counter = await client.get_sellable_rests()
        await message.answer(f'{static.REMAINS}\n{self._remain_counter_to_string(remain_counter)}')

        await BotStates.input_remains.set()
        await message.answer(
            f'{static.SELECT_ITEM}',
            reply_markup=keyboard.create_reply_keyboard_markup((buttons.Buttons.SELECT_REMAINS.value,))
        )

    async def _on_input_remains(self, input_user_remains: containers.InputUserRemains):
        user_hash = self._get_user_hash(input_user_remains.chat_id, input_user_remains.user_id)
        user_data = self._get_user_data(user_hash)
        remain_counter = await user_data.tele2client.get_sellable_rests()
        normalized_remain_counter = self._normalize_remains(input_user_remains, remain_counter)

        remain_counter_str = self._remain_counter_to_string(normalized_remain_counter)
        if normalized_remain_counter != remain_counter:
            message = f'{static.LIMIT_REACHED} {remain_counter_str}'
        else:
            message = f'{static.SELL_COUNT}: {remain_counter_str}'
        await self._dispatcher.bot.send_message(input_user_remains.chat_id, message)
        state = self._dispatcher.current_state(chat=input_user_remains.chat_id, user=input_user_remains.user_id)
        await state.finish()

    def _get_user_hash_by_message(self, message: types.Message) -> str:
        return self._get_user_hash(message.chat.id, message.from_user.id)

    @staticmethod
    def _get_user_hash(chat_id: int, user_id: int) -> str:
        return f'{chat_id}_{user_id}'

    def _update_users_data(self, user_hash: str, tele2client: Tele2Client = None, sms_waiter: event.ValueWaiter = None):
        user_data = self._get_user_data(user_hash)
        user_data.update(tele2client, sms_waiter)
        self._users_data[user_hash] = user_data

    def _get_user_data(self, user_hash: str) -> containers.UserData:
        return self._users_data.get(user_hash, containers.UserData())

    @staticmethod
    def _normalize_remains(
            input_user_remains: containers.InputUserRemains,
            remain_counter: tele2containers.RemainCounter) -> tele2containers.RemainCounter:
        remains = input_user_remains.remains
        return tele2containers.RemainCounter(
            minutes=min(remains.voice, remain_counter.minutes),
            gigabytes=min(remains.internet, int(remain_counter.gigabytes)),
            sms=min(remains.sms, remain_counter.sms)
        )

    @staticmethod
    def _remain_counter_to_string(remain_counter: tele2containers.RemainCounter) -> str:
        return f'{static.INTERNET_REMAINS}: {round(remain_counter.gigabytes, 2)}\n' \
               f'{static.VOICE_REMAINS}: {remain_counter.minutes}\n' \
               f'{static.SMS_REMAINS}: {remain_counter.sms}'
