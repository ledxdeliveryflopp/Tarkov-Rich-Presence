import cProfile
import time

from loguru import logger

from src.analyzer.service import log_analyzer
from src.presence.service import presence_service
from src.settings import settings
from src.utils import find_eft_process


@logger.catch
def start_main_loop() -> None:
    while True:
        if settings.debug is False:
            game_status = find_eft_process()
            if game_status is True:
                if not settings.game_output_log_path:
                    settings.set_output_log_path()
                if not settings.user_uid:
                    log_analyzer.get_user_id()
                presence_service.set_presence()
                time.sleep(settings.refresh_timer)
            else:
                settings.delete_saved_log_path()
                time.sleep(30)
        else:
            if not settings.game_output_log_path:
                settings.set_output_log_path()
            if not settings.user_uid:
                log_analyzer.get_user_id()
            presence_service.set_presence()
            time.sleep(settings.refresh_timer)


@logger.catch
def start_profiler_loop(c_profiler: cProfile.Profile):
    c_profiler.enable()
    start_main_loop()
