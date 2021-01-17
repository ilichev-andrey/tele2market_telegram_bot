import asyncio
from queue import Queue, Empty
from typing import List

from tele2client.client import Tele2Client
from tele2client.exceptions import BaseTele2ClientException
from tele2client.wrappers.logger import LoggerWrap

from executor import configs, containers
from lot.lot_manager import LotManager

TaskQueue = Queue[containers.Task]


class TaskManager(object):
    config: configs.TaskManagerConfig
    queue: TaskQueue
    tasks: List[containers.Task]
    clients: containers.Clients
    lot_manager: LotManager

    def __init__(self, config: configs.TaskManagerConfig, queue: TaskQueue):
        self.config = config
        self.queue = queue
        self.tasks = []
        self.clients = containers.Clients()
        self.lot_manager = LotManager(config.lot_manager_config)

    async def run(self):
        while True:
            await asyncio.sleep(self.config.interval_seconds)
            await self._refresh()
            LoggerWrap().get_logger().info('task manager')
            await self._handle_tasks()

    async def _handle_tasks(self):
        for task in self.tasks:
            await self._handle_task(task)

    async def _handle_task(self, task: containers.Task):
        phone_number = task.tele2client.phone_number
        try:
            task.lots = await self.lot_manager.renew(task.lots, task.summary, self.clients.get(phone_number))
        except BaseTele2ClientException:
            LoggerWrap().get_logger().warning('Не удалось пересоздать лоты')

    async def _refresh(self):
        # берем новые задачи от бота
        tasks = self._load_tasks()
        for task in tasks:
            phone_number = task.tele2client.phone_number
            if self.clients.has(phone_number):
                # В новой задачи получен заново авторизованный клиент, поэтому заменяем на новый
                client = self.clients.get(phone_number)
                await client.close()
            else:
                client = task.tele2client

            client = await self.create_new_client(client)
            self.clients.add(client)
            task.lots.extend(await self.lot_manager.create(task.summary, client))

        self.tasks.extend(tasks)

    @staticmethod
    async def create_new_client(old_client: Tele2Client) -> Tele2Client:
        client = Tele2Client(old_client.phone_number)
        await client.auth_with_params(access_token=old_client.access_token)
        return client

    def _load_tasks(self) -> List[containers.Task]:
        tasks = []
        while True:
            try:
                task = self.queue.get_nowait()
            except Empty:
                return tasks
            else:
                tasks.append(task)
