import yaml
from loguru import logger
from yaml import SafeLoader

from src.const import const
from src.exceptions.service import exception_handler


class Settings:

    def __init__(self):
        self.language: str | None = None
        self.refresh_timer: int | None = None
        self.timer_mode: str | None = None
        self.profiler: str | None = None
        self.log_level: str | None = None
        self.set_settings()

    @property
    @logger.catch(reraise=True)
    def __get_setting_data(self) -> dict:
        with open('settings.yml', encoding='utf-8') as settings_data:
            data = yaml.load(settings_data, Loader=SafeLoader)
        return data

    def __set_lang_settings(self, settings_data: dict) -> None:
        logger.info('Starting set language settings!')
        lang_settings = settings_data.get('language', None)
        if not lang_settings:
            exception_handler.empty_lang_level(setting_info=settings_data)
        if lang_settings not in const.lang.allowed_langs:
            exception_handler.restricted_lang_setting(restricted_lang=lang_settings)
        self.language = lang_settings
        logger.info(f'The installation of the language settings is completed! -> {self.language}')

    def __set_presence_settings(self, settings_data: dict) -> None:
        logger.info('Starting set presence settings!')
        presence_settings: dict | None = settings_data.get('presence', None)
        if not presence_settings:
            exception_handler.empty_presence_level(setting_info=settings_data)
        refresh_time: str | int | None = presence_settings.get('refresh_time', None)
        if not refresh_time:
            err = 'Error while set presence refresh timer, empty refresh timer'
            exception_handler.raise_custom_exception(error_text=err, info=refresh_time)
        self.refresh_timer = int(refresh_time)
        timer_mode = presence_settings.get('timer_mode', None)
        if timer_mode not in const.presence.allowed_timer_mode:
            exception_handler.restricted_presence_timer_mode(restricted_timer=timer_mode)
        self.timer_mode = timer_mode
        logger.info(f'The installation of the presence settings is completed! -> {presence_settings}')

    def __set_application_settings(self, settings_data: dict) -> None:
        logger.info('Starting set application settings!')
        core_settings: dict | None = settings_data.get('core', None)
        if not core_settings:
            exception_handler.empty_application_core_level(setting_info=settings_data)
        logger_level_settings: str | None = core_settings.get('logger_level', None)
        if not logger_level_settings:
            err = 'Error while set application log settings, empty log level'
            exception_handler.raise_custom_exception(error_text=err, info=logger_level_settings)
        if logger_level_settings not in const.application.allowed_loger_levels:
            exception_handler.restricted_logger_level_mode(restricted_level=logger_level_settings)
        self.set_logger(log_level=logger_level_settings)
        self.log_level = logger_level_settings
        profiler_settings: dict | None = core_settings.get('profiler', None)
        if profiler_settings:
            if type(profiler_settings) is bool:
                self.profiler = profiler_settings
        logger.info(f'The installation of the application settings is completed! -> {core_settings}')

    @staticmethod
    def set_logger(log_level: str) -> None:
        logger.info('Starting set Loguru settings!')
        logger.remove()
        logger.add(
            'eft-discord-rich-presence.log',
            format="{time:DD-MM-YYYY at HH:mm:ss} | {level} | {message}",
            level=log_level.upper(),
        )
        logger.info(f'The installation of the Loguru settings is completed! -> {log_level}')

    def __validate_settings_levels(self) -> dict:
        data = self.__get_setting_data
        logger.info(f'Yml settings data: {data}')
        settings_data: dict | None = data.get('settings', None)
        if not settings_data:
            exception_handler.empty_core_settings_level(setting_info=settings_data)
        presence_settings: dict | None = settings_data.get('presence', None)
        if not presence_settings:
            exception_handler.empty_presence_level(setting_info=settings_data)
        core_settings: dict | None = settings_data.get('core', None)
        if not core_settings:
            exception_handler.empty_application_core_level(setting_info=settings_data)
        return settings_data

    @logger.catch(reraise=True)
    def set_settings(self) -> None:
        validated_settings_data = self.__validate_settings_levels()
        self.__set_application_settings(settings_data=validated_settings_data)
        self.__set_presence_settings(settings_data=validated_settings_data)
        self.__set_lang_settings(settings_data=validated_settings_data)


settings = Settings()
