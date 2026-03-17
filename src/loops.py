import cProfile
import time

from loguru import logger

from src.analyzer.service import log_analyzer
from src.presence.service import presence_service
from src.settings import settings
from src.utils import find_eft_process
from pypresence import DiscordError, DiscordNotFound, PipeClosed, InvalidPipe


@logger.catch
def start_main_loop() -> None:
    while True:
        discord_status = presence_service.get_discord_pipe()
        logger.info(f'Discord pipe -> {discord_status}')
        if settings.debug is False:
            game_status = find_eft_process()
            logger.info(f'Game status -> {game_status}')
            if game_status is True and discord_status is not None:
                if not settings.game_output_log_path:
                    settings.set_output_log_path()
                if not settings.user_uid:
                    log_analyzer.get_user_id()
                try:
                    presence_service.set_presence()
                    time.sleep(settings.refresh_timer)
                except (BrokenPipeError, DiscordError, DiscordNotFound, PipeClosed, InvalidPipe, AssertionError) as exc:
                    logger.error(f'Error while set presence -> {exc}')
                    logger.info(f'Trying to disconnect from Discord')
                    presence_service.disconnect_from_discord()
                    presence_service.connect_to_discord()
            else:
                settings.delete_saved_log_path()
                time.sleep(30)
                presence_service.disconnect_from_discord()
                presence_service.connect_to_discord()
        else:
            if discord_status:
                if not settings.game_output_log_path:
                    settings.set_output_log_path()
                if not settings.user_uid:
                    log_analyzer.get_user_id()
                try:
                    presence_service.set_presence()
                    time.sleep(settings.refresh_timer)
                except (BrokenPipeError, DiscordError, DiscordNotFound, PipeClosed, InvalidPipe, AssertionError) as exc:
                    logger.error(f'Error while set presence -> {exc}')
                    logger.info(f'Trying to disconnect from Discord')
                    presence_service.disconnect_from_discord()
                    presence_service.connect_to_discord()
            else:
                logger.debug('Discord pipe is empty')
                time.sleep(5)
                presence_service.disconnect_from_discord()
                presence_service.connect_to_discord()


@logger.catch
def start_profiler_loop(c_profiler: cProfile.Profile):
    c_profiler.enable()
    start_main_loop()
