from typing import Optional, Literal

from loguru import logger
from pypresence import Presence, ActivityType

from src.analyzer.service import log_analyzer
from src.const import const
from src.profile.service import http_grabber
from src.settings import settings


class EftPresenceService(Presence):

    def __init__(self):
        super().__init__(client_id='1441056758645915698')
        self.connect()

    @logger.catch
    def __build_raid_presence_info(self, raid_location: str, location_image: str) -> ...:
        profile_info = http_grabber.grab_user_profile()
        state = const.presence.in_raid_state[settings.language]
        faction = None
        if profile_info:
            username = profile_info.info.nickname
            level = profile_info.info.experience
            prestige = profile_info.info.prestige_level
            faction = profile_info.info.side.lower()
            presence_details = f'{state} {username}({level} lvl)({prestige} prestige)'
        if not profile_info:
            presence_details = const.presence.in_raid[settings.language]
        presence_state = f'{state} {raid_location}'
        logger.debug(f'Presence details -> {presence_details}')
        logger.debug(f'Presence state -> {presence_state}')
        info = {
            'state': presence_state,
            'details': presence_details,
            'large_image': location_image,
            'small_image': faction or 'Empty',
            'large_text': raid_location,
            'small_text': faction or 'Empty',
        }
        logger.debug(f'Presence info -> {info}')
        return info

    @logger.catch
    def __build_lobby_presence_info(self) -> ...:
        profile_info = http_grabber.grab_user_profile()
        presence_details = None
        faction = None
        state = const.presence.in_lobby[settings.language]
        if profile_info:
            username = profile_info.info.nickname
            level = profile_info.info.experience
            prestige = profile_info.info.prestige_level
            faction = profile_info.info.side.lower()
            presence_details = f'{state} {username}({level} lvl)({prestige} prestige)'
        if not profile_info:
            presence_details = state
        presence_state = const.presence.in_lobby_state[settings.language]
        logger.debug(f'Presence details -> {presence_details}')
        logger.debug(f'Presence state -> {presence_state}')
        info = {
            'state': presence_state,
            'details': presence_details,
            'large_image': 'Empty',
            'small_image': faction or 'Empty',
            'large_text': 'Empty',
            'small_text': faction or 'Empty',
        }
        logger.debug(f'Presence info -> {info}')
        return info

    @logger.catch
    def __set_presence(
            self,
            game_state: Literal['raid', 'lobby'],
            raid_location: Optional[str] = None,
            location_image: Optional[str] = None,
    ) -> None:
        logger.info(f'Setting {game_state} presence...')
        logger.debug(f'Game state -> {game_state}')
        if game_state == 'raid':
            presence_info = self.__build_raid_presence_info(
                raid_location=raid_location, location_image=location_image,
            )
        elif game_state == 'lobby':
            presence_info = self.__build_lobby_presence_info()
        state = presence_info['state']
        details = presence_info['details']
        large_image = presence_info['large_image']
        small_image = presence_info['small_image']
        large_text = presence_info['large_text']
        small_text = presence_info['small_text']
        log_analyzer.update_group_count()
        self.update(
            activity_type=ActivityType.PLAYING,
            details=details,
            state=state,
            party_size=[log_analyzer.current_player_count, 5],
            large_image=large_image,
            large_text=large_text,
            small_text=small_text,
            small_image=small_image,
        )
        logger.info(f'{game_state} presence set successfully!')

    @logger.catch
    def set_presence(self):
        logger.info('---------------SET PRESENCE---------------')
        raid_location, location_image = log_analyzer.get_last_raid_location()
        if not raid_location:
            self.__set_presence(game_state='lobby')
            return
        raid_finish = log_analyzer.get_disconnect_message()
        if raid_finish is True:
            self.__set_presence(game_state='lobby')
        else:
            self.__set_presence(
                game_state='raid',
                raid_location=raid_location,
                location_image=location_image,
            )
        logger.info('---------------PRESENCE SET FINISH---------------')


presence_service = EftPresenceService()
