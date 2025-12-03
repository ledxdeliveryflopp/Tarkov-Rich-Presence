import time

from src.analyzer.service import log_analyzer
from src.presence.service import presence_service
from src.profile.service import http_grabber
from src.settings import settings

if __name__ == '__main__':
    settings.set_logger()
    settings.set_settings()
    log_analyzer.get_user_id()
    http_grabber.grab_user_profile()
    while True:
        if not settings.user_uid:
            log_analyzer.get_user_id()
        presence_service.set_presence()
        time.sleep(settings.refresh_timer)
