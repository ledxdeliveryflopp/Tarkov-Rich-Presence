import cProfile
import time

from loguru import logger

from src.analyzer.service import log_analyzer
from src.github.version import version_checker
from src.presence.service import presence_service
from src.settings import settings
from src.utils import find_eft_process


@logger.catch
def start_main_loop() -> None:
    while True:
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


@logger.catch
def start_profiler_loop():
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        start_main_loop()
    except KeyboardInterrupt:
        logger.debug('Keyboard Interrupt!')
        profiler.disable()
        profiler.dump_stats(f'all_functions{time.time()}.prof')


if __name__ == '__main__':
    settings.set_logger()
    version_checker.check_version()
    settings.set_settings()
    if settings.profiler is True:
        start_profiler_loop()
    else:
        start_main_loop()
