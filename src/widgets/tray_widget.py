import webbrowser

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QApplication, QSystemTrayIcon, QMenu
from loguru import logger

from src.const import const
from src.github.version import version_checker
from src.settings import settings
from src.workers import ThreadWorker


class TrayWidget(QWidget):

    @logger.catch
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.icon = QIcon(const.widgets.icon_file)
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.icon)
        self.tray.setVisible(True)

        self.menu = QMenu()
        self.current_version = QAction(f'Версия: {settings.app_version}')
        self.update_action = QAction('Проверка версии...', self)
        self.current_version.triggered.connect(self.open_release_page)
        self.menu.addAction(self.current_version)
        self.menu.addAction(self.update_action)
        self.tray.setContextMenu(self.menu)

        self.update_worker = ThreadWorker(task=self.check_version)
        self.update_worker.start()

    def check_version(self) -> None:
        installer_exist = version_checker.check_installer()
        if installer_exist is False:
            self.update_action.setText(f'Не найден установщик, обновление невозможно')
        else:
            message, result = version_checker.check_version()
            self.update_action.setText(message)
            if result is True:
                self.update_action.triggered.connect(self.update_app)
                self.update_action.triggered.connect(version_checker.open_installer)
                self.menu.addAction(self.update_action)
                self.tray.setContextMenu(self.menu)

    def update_app(self) -> None:
        logger.info('Closing app for update.')
        installer_status = version_checker.open_installer()
        if installer_status is True:
            self.app.exit()
        else:
            self.update_action.setText(f'Не найден установщик, обновление невозможно')

    @logger.catch
    def open_release_page(self) -> None:
        logger.info(f'open release page -> {settings.current_version_html}')
        webbrowser.open(url=settings.current_version_html)
