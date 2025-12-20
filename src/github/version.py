import json
import os
import sys

from loguru import logger
from packaging.version import Version

from src.github.api import GitHubApi
from src.github.utils import single_user_input


class VersionChecker(GitHubApi):

    def __init__(self):
        super().__init__()

    @staticmethod
    def __get_version_from_manifest():
        with open('release_manifest.json', 'r') as json_data:
            data = json.load(json_data)
            return data['tag']

    def __compare_version(self, latest_version: str) -> bool:
        current_version = self.__get_version_from_manifest()
        logger.debug(f'Current version -> {current_version}')
        logger.debug(f'Latest version -> {latest_version}')
        return Version(current_version) < Version(latest_version)

    # TODO: временное решение
    @single_user_input(question='Обновить? (y/n): ')
    @logger.catch
    def __open_installer(self, question: str) -> None:
        if question == 'y':
            file_path = rf'{os.getcwd()}\installer.exe'
            os.startfile(file_path)
            sys.exit(0)
        elif question == 'n':
            return None
        else:
            self.__open_installer()

    def check_version(self) -> None:
        latest_version = self.get_latest_release_version()
        compare_result = self.__compare_version(latest_version=latest_version)
        if compare_result is True:
            print('Вышла новая версия!')
            self.__open_installer()
        else:
            pass


version_checker = VersionChecker()
