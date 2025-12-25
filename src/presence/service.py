import time
from typing import Optional, Literal

from loguru import logger
from pypresence import Presence, ActivityType

from src.analyzer.service import log_analyzer
from src.const import const
from src.profile.service import http_grabber
from src.settings import settings
from src.storage import storage


class EftPresenceService(Presence):

    def __init__(self):
        super().__init__(client_id='1441056758645915698')
        self.connect()

    @logger.catch
    def __build_presence_info(
            self,
            game_state: Literal['raid', 'lobby'],
            raid_location: Optional[str] = None,
            location_image: Optional[str] = None,
    ) -> dict:
        profile_info = http_grabber.grab_user_profile()
        if game_state == 'raid':
            presence_state = f'{const.presence.in_raid_state[settings.language]}({settings.game_mode}): {raid_location}'
            presence_details = f'{presence_state}'
        else:
            presence_state = const.presence.in_lobby_state[settings.language]
            presence_details = const.presence.in_lobby[settings.language]
        faction = None
        if profile_info:
            username = profile_info.info.nickname
            level = profile_info.info.experience
            faction = profile_info.info.side.lower()
            prestige = profile_info.info.prestige_level
            first_details = f'{username}, {level} {const.presence.level_details[settings.language]}'
            if settings.show_zero_prestige is True or prestige > 0:
                second_details = f'{prestige} {const.presence.prestige_details[settings.language]}'
                presence_details = f'{first_details}, {second_details}'
            else:
                presence_details = first_details
        logger.debug(f'Presence details -> {presence_details}')
        logger.debug(f'Presence state -> {presence_state}')
        info = {
            'state': presence_state,
            'details': presence_details,
            'large_image': location_image if location_image != 'Unknown location' else 'logo',
            'small_image': faction if faction else 'Empty',
            'large_text': raid_location if raid_location else 'Escape from Tarkov',
            'small_text': faction if faction else 'Empty',
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
            presence_info = self.__build_presence_info(
                raid_location=raid_location, location_image=location_image, game_state='raid',
            )
        else:
            location_image = 'logo'
            presence_info = self.__build_presence_info(
                game_state='lobby', location_image=location_image,
            )
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
            start=storage.start_raid_time
        )
        logger.info(f'{game_state} presence set successfully!')

    @logger.catch
    def set_presence(self):
        logger.info('---------------SET PRESENCE---------------')
        raid_location, location_image = log_analyzer.get_last_raid_location()
        raid_finish = log_analyzer.get_disconnect_message()
        if not raid_location or raid_finish is True:
            self.__set_presence(game_state='lobby')
        else:
            self.__set_presence(
                game_state='raid',
                raid_location=raid_location,
                location_image=location_image,
            )
        logger.info('---------------PRESENCE SET FINISH---------------')


presence_service = EftPresenceService()
