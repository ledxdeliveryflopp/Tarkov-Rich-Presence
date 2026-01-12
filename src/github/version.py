import os

from loguru import logger
from packaging.version import Version

from src.github.api import GitHubApi
from src.settings import settings


class VersionChecker(GitHubApi):

    def __init__(self):
        super().__init__()

    @staticmethod
    def __compare_version(latest_version: str) -> bool:
        current_version = settings.app_version
        logger.debug(f'Current version -> {current_version}')
        logger.debug(f'Latest version -> {latest_version}')
        return Version(current_version) < Version(latest_version)

    @logger.catch
    def open_installer(self) -> None:
        file_path = rf'{os.getcwd()}\installer.exe'
        installer_exist = os.path.exists(file_path)
        if installer_exist is True:
            os.startfile(file_path)
        else:
            logger.error(f'Installer not found at -> {file_path}')
            pass

    @logger.catch
    def check_installer(self) -> bool:
        installer_path = rf'{os.getcwd()}\installer.exe'
        installer_exist = os.path.exists(installer_path)
        if installer_exist is True:
            logger.info(f'Installer exist at path -> {installer_path}')
            return True
        else:
            logger.info(f'Installer not exist at path -> {installer_path}')
            return False

    def check_version(self) -> (str, bool):
        try:
            latest_version = self.get_latest_release_version()
            compare_result = self.__compare_version(latest_version=latest_version)
            if compare_result is True:
                return f'Доступно обновление до: {latest_version}', True
            else:
                return 'Актуальная версия', False
        except Exception as exc:
            logger.error(exc)
            return 'Не удалось проверить версию', False


version_checker = VersionChecker()
