from typing import Any, Callable, Coroutine

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import containers
from bot.handlers.user_input import validator
from bot.view import buttons, static

OnInputDoneType = Callable[[containers.InputUserRemains], Coroutine[Any, Any, None]]


class InputRemainStates(StatesGroup):
    input_internet = State()
    input_voice = State()
    input_sms = State()


class InputRemainsHandler(object):
    _dispatcher: Dispatcher
    _on_input_done: OnInputDoneType

    def __init__(self, dispatcher: Dispatcher, on_input_done: OnInputDoneType):
        self._dispatcher = dispatcher
        self._on_input_done = on_input_done

    def init(self, start_state):
        self._dispatcher.register_message_handler(
            self._start,
            lambda message: message.text == buttons.Buttons.SELECT_REMAINS.value,
            state=start_state
        )
        self._dispatcher.register_message_handler(
            self._input_internet,
            state=InputRemainStates.input_internet,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_message_handler(
            self._input_voice,
            state=InputRemainStates.input_voice,
            content_types=types.ContentTypes.TEXT
        )
        self._dispatcher.register_message_handler(
            self._input_sms,
            state=InputRemainStates.input_sms,
            content_types=types.ContentTypes.TEXT
        )

    async def _start(self, message: types.Message):
        await InputRemainStates.input_internet.set()
        await message.answer(self._get_answer_message(static.INTERNET_REMAINS))

    async def _input_internet(self, message: types.Message, state: FSMContext):
        if not validator.is_valid_number(message.text):
            await message.answer(f'{static.FAILED_INPUT}. {self._get_answer_message(static.INTERNET_REMAINS)}')

        await state.update_data(internet=int(message.text))
        await InputRemainStates.input_voice.set()
        await message.answer(self._get_answer_message(static.VOICE_REMAINS))

    async def _input_voice(self, message: types.Message, state: FSMContext):
        if not validator.is_valid_number(message.text):
            await message.answer(f'{static.FAILED_INPUT}. {self._get_answer_message(static.VOICE_REMAINS)}')

        await state.update_data(voice=int(message.text))
        await InputRemainStates.input_sms.set()
        await message.answer(self._get_answer_message(static.SMS_REMAINS))

    async def _input_sms(self, message: types.Message, state: FSMContext):
        if not validator.is_valid_number(message.text):
            await message.answer(f'{static.FAILED_INPUT}. {self._get_answer_message(static.SMS_REMAINS)}')

        await state.update_data(sms=int(message.text))
        await self._done(message.chat.id, message.from_user.id, state)

    async def _done(self, chat_id: int, user_id: int, state: FSMContext):
        input_data = await state.get_data()
        await state.finish()

        await self._on_input_done(containers.InputUserRemains(
            chat_id=chat_id,
            user_id=user_id,
            remains=containers.InputRemains(
                internet=input_data.get('internet', 0),
                voice=input_data.get('voice', 0),
                sms=input_data.get('sms', 0)
            )
        ))

    @staticmethod
    def _get_answer_message(remains_name: str) -> str:
        return f'{static.SELECT_REMAINS} {remains_name.upper()} ({static.REMAINS_FORMAT}):'
