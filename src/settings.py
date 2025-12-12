import os

import yaml
from loguru import logger
from yaml import SafeLoader

from src.const import const
from src.schemas import SettingsSchemas


class Settings:

    def __init__(self):
        self.language: str | None = None
        self.refresh_timer: int | None = None
        self.show_zero_prestige: bool | None = None
        self.game_mode: str | None = None
        self.timer_mode: str | None = None
        self.profiler: str | None = None
        self.log_level: str | None = None
        self.user_uid: str | None = None
        self.loguru_log_file: str | None = None
        self.loguru_diagnostic: bool | None = None
        self.game_log_folder_path: str | None = None
        self.game_output_log_path: str | None = None
        self.locations_data: dict | None = None
        self.deque_search: bool | None = None
        self.deque_max_depth: int | None = None

    @property
    @logger.catch(reraise=True)
    def __get_setting_data(self) -> dict:
        with open('settings.yml', encoding='utf-8') as settings_data:
            data = yaml.load(settings_data, Loader=SafeLoader)
        return data

    @logger.catch
    def __set_locations_data(self) -> None:
        logger.info('Starting to load locations data!')
        with open('locations.yml', encoding='utf-8') as locations_data:
            data = yaml.load(locations_data, Loader=SafeLoader)
            self.locations_data = data
            logger.debug(f'Locations info -> {self.locations_data}')
        logger.info('Finished loading locations data!')

    def __set_lang_settings(self, settings_data: SettingsSchemas) -> None:
        logger.info('Starting set language settings...')
        lang_settings = settings_data.settings.language
        self.language = lang_settings
        logger.debug(f'The installation of the language settings is completed -> {self.language}')
        logger.info('The installation of the language settings is completed!')

    def __set_presence_settings(self, settings_data: SettingsSchemas) -> None:
        logger.info('Starting set presence settings...')
        presence_settings = settings_data.settings.presence
        refresh_time = presence_settings.refresh_time
        timer_mode = presence_settings.timer_mode
        zero_prestige = presence_settings.show_zero_prestige
        self.refresh_timer = refresh_time
        self.timer_mode = timer_mode
        self.show_zero_prestige = zero_prestige
        logger.debug(f'The installation of the presence settings is completed -> {presence_settings.__dict__}')
        logger.info('The installation of the presence settings is completed!')

    def __set_application_settings(self, settings_data: SettingsSchemas) -> None:
        logger.info('Starting set application settings...')
        application_settings = settings_data.settings.core
        game_log_path_settings = application_settings.log_folder_path
        self.game_log_folder_path = game_log_path_settings
        self.deque_search = application_settings.deque_search
        self.deque_max_depth = application_settings.deque_max_depth
        logger.debug(f'The installation of the application settings is completed -> {application_settings.__dict__}')
        logger.info('The installation of the application settings is completed!')

    def __set_output_log_path(self) -> None:
        logger.info('Start searching for output logs...')
        last_big_timestamp = None
        last_dir_name = None
        with os.scandir(self.game_log_folder_path) as it:
            for directory in it:
                if directory.is_dir():
                    dir_name = directory.name
                    creation_timestamp = directory.stat().st_ctime
                    if not last_big_timestamp:
                        last_big_timestamp = creation_timestamp
                        last_dir_name = dir_name
                    if creation_timestamp > last_big_timestamp:
                        last_big_timestamp = creation_timestamp
                        last_dir_name = dir_name
        current_output_logs = os.listdir(f'{self.game_log_folder_path}/{last_dir_name}')
        game_log = [i for i in current_output_logs if 'output' in i]
        if len(game_log) == 0:
            logger.error(f'No output logs found in {self.game_log_folder_path}/{last_dir_name} -> {game_log}')
        self.game_output_log_path = f'{self.game_log_folder_path}/{last_dir_name}/{game_log[0]}'
        logger.debug(f'EFT output log path -> {self.game_output_log_path}')
        logger.info(f'EFT output log was found!')

    def __validate_settings_levels(self) -> SettingsSchemas:
        data = self.__get_setting_data
        logger.debug(f'Yml settings data: {data}')
        validated_settings = SettingsSchemas(**data)
        return validated_settings

    def set_logger(self) -> None:
        try:
            with open('logger.yml', encoding='utf-8') as settings_data:
                data = yaml.load(settings_data, Loader=SafeLoader)['logger']
            self.log_level = data.get('level', 'DEBUG').upper()
            self.loguru_log_file = data.get('file', 'eft-discord-rich-presence.log')
            self.loguru_diagnostic = data.get('diagnostic', False)
        except FileNotFoundError:
            self.log_level = 'DEBUG'
            self.loguru_log_file = 'eft-discord-rich-presence.log'
            self.loguru_diagnostic = True
        finally:
            logger.add(
                self.loguru_log_file,
                format="{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}",
                level=self.log_level,
                diagnose=self.loguru_diagnostic,
            )

    @logger.catch
    def __build_level_range(self) -> None:
        logger.info('Building level range...')
        level_range = const.levels.range
        for key, value in level_range.items():
            second_level_index = key + 1
            second_level = level_range.get(second_level_index, None)
            if not second_level:
                break
            actual_level_exp_req = value['full_exp']
            second_level_exp_range = second_level['last_exp']
            second_level_exp_req = actual_level_exp_req + second_level_exp_range
            const.levels.range[second_level_index]['full_exp'] = second_level_exp_req
        logger.debug(f'Levels range -> {const.levels.range}')
        logger.info('Levels range built!')

    @logger.catch(reraise=True)
    def set_settings(self) -> None:
        logger.info('Start installing settings...')
        validated_settings_data = self.__validate_settings_levels()
        self.__set_application_settings(settings_data=validated_settings_data)
        self.__set_presence_settings(settings_data=validated_settings_data)
        self.__set_lang_settings(settings_data=validated_settings_data)
        self.__set_output_log_path()
        self.__build_level_range()
        self.__set_locations_data()
        logger.info('Finished installing settings.')

    def store_user_id(self, user_id: str) -> None:
        logger.info('Storing user uid!')
        self.user_uid = user_id
        logger.info(f'The user uid is stored successfully!')
        logger.debug(f'The user uid is stored -> {self.user_uid}')


settings = Settings()
