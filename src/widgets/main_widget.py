import cProfile
import time
from typing import Optional

from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import QWidget, QSystemTrayIcon, QApplication, QVBoxLayout, QLabel
from loguru import logger

from src.loops import start_profiler_loop, start_main_loop
from src.settings import settings
from src.widgets.tray_widget import TrayWidget
from src.workers import ThreadWorker


class MainWidget(QWidget):

    def __init__(self, app: QApplication, c_profiler: Optional[cProfile.Profile] = None):
        super().__init__()
        self.worker: ThreadWorker | None = None
        self.setWindowTitle('Я мутирую')
        layout = QVBoxLayout()
        self.label = QLabel('А тут еще ничего нет')
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.app = app
        self.c_profiler = c_profiler
        self.tray_widget = TrayWidget(self.app)
        self.tray_widget.tray.activated.connect(self.show_main_widget)

        self.quit_action = QAction('Закрыть приложение', self)
        self.tray_widget.menu.addAction(self.quit_action)
        self.quit_action.triggered.connect(self.stop_app)
        self.tray_widget.tray.setContextMenu(self.tray_widget.menu)

    def start_main_loop(self) -> None:
        self.worker = ThreadWorker(task=self.main_loop)
        self.worker.start()

    @logger.catch
    def show_main_widget(self, reason) -> None:
        logger.info(f'Tray activate reason -> {reason}')
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    @logger.catch
    def main_loop(self) -> None:
        if settings.profiler is True:
            start_profiler_loop(c_profiler=self.c_profiler)
        else:
            start_main_loop()

    def stop_app(self) -> None:
        if settings.profiler is True:
            self.c_profiler.disable()
            self.c_profiler.dump_stats(f'all_functions{time.time()}.prof')
            logger.debug('saving profiler dump')
        logger.info('close application')
        self.worker.stop_task()
        self.app.exit()
