import time

from src.presence.service import presence_service
from src.settings import settings

if __name__ == '__main__':
    while True:
        presence_service.set_presence()
        time.sleep(settings.refresh_timer)
