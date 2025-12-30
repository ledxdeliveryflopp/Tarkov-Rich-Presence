import cProfile
import signal
import sys
import time

from loguru import logger

from src.analyzer.service import log_analyzer
from src.github.version import version_checker
from src.presence.service import presence_service
from src.settings import settings
from src.utils import find_eft_process


def create_signal_handler(c_profiler: cProfile.Profile):
    def signal_handler(sig, frame):
        print("Закрытие приложения...")
        logger.debug('Signal handler')
        logger.info(f'Handler settings -> {settings.__dict__}')
        if settings.profiler is True:
            c_profiler.disable()
            c_profiler.dump_stats(f'all_functions{time.time()}.prof')
            logger.debug('saving profiler dump')
        sys.exit(0)
    return signal_handler


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


if __name__ == '__main__':
    settings.set_logger()
    version_checker.check_version()
    settings.set_settings()
    profiler = cProfile.Profile()
    handler = create_signal_handler(c_profiler=profiler)
    signal.signal(signal.SIGINT, handler)
    if settings.profiler is True:
        start_profiler_loop(c_profiler=profiler)
    else:
        start_main_loop()
