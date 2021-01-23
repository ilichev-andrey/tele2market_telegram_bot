from tele2client import containers as tele2containers

from bot.view import static


def remain_counter_to_string(remain_counter: tele2containers.RemainCounter) -> str:
    return f'{static.INTERNET_REMAINS}: {round(remain_counter.gigabytes, 2)}\n' \
           f'{static.VOICE_REMAINS}: {remain_counter.minutes}\n' \
           f'{static.SMS_REMAINS}: {remain_counter.sms}'
