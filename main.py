import asyncio
import json
import logging
import os
import threading

from bot.service import Service
from tele2client.wrappers import logger
from executor.configs import TaskManagerConfig, LotManagerConfig, MinLotPrice, Price
from executor.task_manager import TaskManager, TaskQueue, Queue

CONFIG_FILE = 'config.js'


async def manage_lots(config: TaskManagerConfig, task_queue: TaskQueue):
    manager = TaskManager(config, task_queue)
    await manager.run()


async def start(config, task_queue):
    await asyncio.gather(asyncio.ensure_future(manage_lots(config, task_queue)))


def run_thread(config, task_queue):
    asyncio.run(start(config, task_queue))


def main():
    with open(CONFIG_FILE) as fin:
        config = json.load(fin)

    logger.create(config['log_file'], logging.INFO)

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
    thread = threading.Thread(target=run_thread, args=(config, task_queue))
    thread.start()

    service = Service(os.getenv('TELEGRAM_API_TOKEN'), task_queue)
    service.init()
    service.run()

    thread.join()


if __name__ == '__main__':
    main()
