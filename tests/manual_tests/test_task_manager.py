import asyncio
import json
import logging
import os

from tele2client import containers, time_utils
from tele2client.wrappers import logger
from tele2client.client import Tele2Client

from executor.containers import Task, TaskSummary
from executor.configs import TaskManagerConfig, LotManagerConfig, MinLotPrice, Price
from executor.task_manager import TaskManager, TaskQueue, Queue

PHONE_NUMBER = os.getenv('PHONE_NUMBER')
LOG_FILE = '/Users/andreyilichev/andrey/projects/python/tele2/tele2market_tg_bot/logs/test_task_manager.log'
AUTH_FILE = '/Users/andreyilichev/andrey/projects/python/tele2/tele2market_tg_bot/tmp/auth.json'


async def manage_lots(config: TaskManagerConfig, task_queue: TaskQueue):
    client = await auth()
    task_queue.put_nowait(Task(
        tele2client=client,
        lots=[],
        summary=TaskSummary(
            gigabyte_count=2,
            minute_count=100,
            sms_count=0
        )
    ))

    manager = TaskManager(config, task_queue)
    await manager.run()


async def start(config, task_queue):
    await asyncio.gather(asyncio.ensure_future(manage_lots(config, task_queue)))


async def sms_code_getter():
    return input()


async def auth() -> Tele2Client:
    client = Tele2Client(PHONE_NUMBER)

    if os.path.isfile(AUTH_FILE):
        with open(AUTH_FILE) as fin:
            data = json.load(fin)
        await client.auth_with_params(containers.AccessToken(
            token=data['token'],
            expired_dt=time_utils.timestamp2datetime(data['expired_dt'])
        ))
        return client

    if await client.auth(sms_code_getter):
        with open(AUTH_FILE, 'w') as fout:
            json.dump(
                {'token': client.access_token.token, 'expired_dt': client.access_token.expired_dt.timestamp()}, fout
            )

    return client


def main():
    logger.create(LOG_FILE, logging.INFO)

    config = TaskManagerConfig(
        interval_seconds=30,
        lot_manager_config=LotManagerConfig(
            internet_life_time_minutes=2,
            voice_life_time_minutes=2,
            sms_life_time_minutes=2,
            prices=MinLotPrice(
                gigabyte=Price(1, 15),
                minutes=Price(50, 40),
                sms=Price(50, 25)
            )
        )
    )

    task_queue = Queue()
    asyncio.run(start(config, task_queue))


if __name__ == '__main__':
    main()
