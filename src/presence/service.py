from loguru import logger
from pypresence import Presence, ActivityType

from src.analyzer.service import log_analyzer
from src.const import const
from src.settings import settings


class EftPresenceService(Presence):

    def __init__(self):
        super().__init__(client_id='1441056758645915698')
        self.connect()

    @logger.catch
    def __set_raid_presence(self, raid_location: str, location_image: str):
        logger.info('Setting raid presence...')
        presence_details = const.presence.in_raid[settings.language]
        presence_state_part = const.presence.location[settings.language]
        presence_state = f'{presence_state_part} {raid_location}'
        logger.debug(f'Presence details -> {presence_details}')
        logger.debug(f'Presence state -> {presence_state}')
        self.update(
            activity_type=ActivityType.PLAYING,
            details=presence_details,
            state=presence_state,
            party_size=[log_analyzer.current_player_count, 5],
            large_image=location_image,
        )
        logger.info('Raid presence set successfully!')

    @logger.catch
    def __set_lobby_presence(self):
        logger.info('Setting lobby presence...')
        presence_details = const.presence.in_lobby[settings.language]
        presence_state = const.presence.in_lobby_state[settings.language]
        logger.debug(f'Presence details -> {presence_details}')
        logger.debug(f'Presence state -> {presence_state}')
        self.update(
                activity_type=ActivityType.PLAYING,
                details=presence_details,
                state=presence_state,
                party_size=[log_analyzer.current_player_count, 5],
            )
        logger.info('Lobby presence set successfully!')

    @logger.catch
    def set_presence(self):
        logger.info('---------------SET PRESENCE---------------')
        raid_location, location_image = log_analyzer.get_last_raid_location()
        if not raid_location:
            log_analyzer.update_group_count()
            self.__set_lobby_presence()
            return
        log_analyzer.update_group_count()
        raid_finish = log_analyzer.get_disconnect_message()
        if raid_finish is True:
            self.__set_lobby_presence()
        else:
            self.__set_raid_presence(raid_location=raid_location, location_image=location_image)
        logger.info('---------------PRESENCE SET FINISH---------------')


presence_service = EftPresenceService()
