from loguru import logger
from pypresence import Presence, ActivityType

from src.analyzer.service import log_analyzer


class EftPresenceService(Presence):

    def __init__(self):
        super().__init__(client_id='1441056758645915698')
        self.connect()

    @logger.catch
    def set_raid_presence(self, raid_location: str):
        logger.info('Setting raid presence...')
        self.update(
            activity_type=ActivityType.PLAYING,
            details='В Рейде',
            state=f'Локация: {raid_location}',
            party_size=[log_analyzer.current_player_count, 5],
        )
        logger.info('Raid presence set successfully!')

    @logger.catch
    def set_lobby_presence(self):
        logger.info('Setting lobby presence...')
        self.update(
                activity_type=ActivityType.PLAYING,
                details='В Схроне',
                state=f'Чиллит',
                party_size=[log_analyzer.current_player_count, 5],
            )
        logger.info('Lobby presence set successfully!')

    @logger.catch
    def set_presence(self):
        logger.info('---------------SET PRESENCE---------------')
        raid_location = log_analyzer.get_last_raid_location()
        if not raid_location:
            pass
        log_analyzer.delete_player_in_group()
        log_analyzer.add_new_player_in_group()
        raid_finish = log_analyzer.get_disconnect_message()
        if raid_finish is True:
            self.set_lobby_presence()
        else:
            self.set_raid_presence(raid_location=raid_location)
        logger.info('---------------PRESENCE SET FINISH---------------')


presence_service = EftPresenceService()
