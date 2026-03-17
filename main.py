import cProfile
import os

from PySide6.QtWidgets import QApplication
from loguru import logger

from src.settings import settings
from src.widgets.main_widget import MainWidget


@logger.catch
def application_setup(c_profiler: cProfile.Profile):
    app = QApplication([])
    settings.set_app_version()
    main = MainWidget(app=app, c_profiler=c_profiler)
    app.setQuitOnLastWindowClosed(False)
    settings.set_settings()
    main.start_main_loop()
    app.exec()


if __name__ == '__main__':
    settings.set_logger()
    logger.info(f'App started from -> {os.getcwd()}')
    profiler = cProfile.Profile()
    application_setup(c_profiler=profiler)
