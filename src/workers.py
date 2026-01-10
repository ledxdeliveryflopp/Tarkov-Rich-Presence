from PySide6.QtCore import QThread
from loguru import logger


class ThreadWorker(QThread):

    def __init__(self, task: callable):
        super().__init__()
        self.task = task
        self.thread_name = None

    @logger.catch
    def run(self) -> None:
        thread_name = f'thread_{self.task.__name__}'
        self.thread_name = thread_name
        self.setObjectName(thread_name)
        logger.debug(f'Thread name -> {thread_name}')
        logger.debug(f'Thread -> {self.currentThread()} started')
        logger.debug(f'Task -> {self.task.__name__}')
        self.task()

    def stop_task(self) -> None:
        self.terminate()
        logger.debug(f'thread name: {self.thread_name} killed')
