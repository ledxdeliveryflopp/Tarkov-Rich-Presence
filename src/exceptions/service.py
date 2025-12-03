from typing import Any, Optional

from loguru import logger

from src.const import const


class ExceptionsService:

    @staticmethod
    def empty_core_settings_level(setting_info: Any):
        logger.error(f'Empty main settings level -> {setting_info}')
        raise Exception('Empty main settings level')

    @staticmethod
    def empty_lang_level(setting_info: Any):
        logger.error(f'Empty language settings level -> {setting_info}')
        raise Exception('Empty language settings level')

    @staticmethod
    def empty_presence_level(setting_info: Any):
        logger.error(f'Empty presence settings level -> {setting_info}')
        raise Exception('Empty presence settings level')

    @staticmethod
    def empty_application_core_level(setting_info: Any):
        logger.error(f'Empty core settings level -> {setting_info}')
        raise Exception('Empty application core settings level')

    @staticmethod
    def empty_application_log_path(setting_info: Any):
        logger.error(f'Empty log path settings level -> {setting_info}')
        raise Exception('Empty application log path settings level')

    @staticmethod
    def restricted_lang_setting(restricted_lang: Any):
        logger.error(f'Error while set -> {restricted_lang}, allowed langs -> {const.lang.allowed_langs}')
        raise Exception('Trying to set restricted lang')

    @staticmethod
    def restricted_presence_timer_mode(restricted_timer: Any):
        logger.error(f'Error while set -> {restricted_timer}, allowed timers -> {const.presence.allowed_timer_mode}')
        raise Exception('Trying to set restricted timer mode')

    @staticmethod
    def restricted_logger_level_mode(restricted_level: Any):
        logger.error(
            f'Error while set -> {restricted_level}, allowed levels -> {const.application.allowed_loger_levels}',
        )
        raise Exception('Trying to set restricted logger level')

    @staticmethod
    def raise_custom_exception(error_text: str, info: Any):
        logger.error(f'{error_text} -> {info}')
        raise Exception(error_text)


exception_handler = ExceptionsService()
