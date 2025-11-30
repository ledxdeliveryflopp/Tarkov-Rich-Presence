import os
from typing import Literal

import yaml
from loguru import logger
from yaml import SafeLoader

from src.settings import settings


class LogAnalyzer:

    def __init__(self):
        self.main_log_dir = 'Logs'
        self.current_output_logs: str | None = None
        self.last_game_server: str | None = None
        self.current_player_count: int = 1
        self.current_player_name: set[str] | None = None
        self.last_game_log_index: int | None = None
        self.game_ignores_indexes: set = set()
        self.disconnect_ignores_indexes: set = set()
        self.last_game_log_finish_index: int | None = None
        self.__get_output_log_path()

    def __get_output_log_path(self) -> None:
        logger.info('Start searching for output logs...')
        last_big_timestamp = None
        last_dir_name = None
        with os.scandir(self.main_log_dir) as it:
            for directory in it:
                if directory.is_dir():
                    dir_name = directory.name
                    creation_timestamp = directory.stat().st_ctime
                    if not last_big_timestamp:
                        last_big_timestamp = creation_timestamp
                        last_dir_name = dir_name
                    if creation_timestamp > last_big_timestamp:
                        last_big_timestamp = creation_timestamp
                        last_dir_name = dir_name
        current_output_logs = os.listdir(f'{self.main_log_dir}/{last_dir_name}')
        game_log = [i for i in current_output_logs if 'output' in i]
        if len(game_log) == 0:
            logger.error(f'No output logs found in {self.main_log_dir}/{last_dir_name} -> {game_log}')
        self.current_output_logs = f'{self.main_log_dir}/{last_dir_name}/{game_log[0]}'
        logger.debug(f'EFT output log path: {self.current_output_logs}')
        logger.info(f'EFT output log was found!')

    @staticmethod
    @logger.catch
    def __get_location_name(location_tech_name: str, lang: Literal['ru', 'en']) -> str:
        with open('locations.yml', encoding='utf-8') as locations_data:
            data = yaml.load(locations_data, Loader=SafeLoader)
            formated_name = location_tech_name.replace(' ', '')
            return data['locations'][formated_name][lang]

    @staticmethod
    def __debug_raid_log(
            profile_uid: str,
            raid_mode: str,
            last_game_server: str,
            tech_location: str,
            server_sid: str,
            game_mode: str,
            short_game_id: str,
    ) -> None:
        logger.debug('---------------------------RAID DEBUG INFO START---------------------------')
        logger.debug(f'Profile ID: {profile_uid}')
        logger.info(f'Raid Mode: {raid_mode}')
        logger.debug(f'Server IP:PORT: {last_game_server}')
        logger.debug(f'Tech Location: {tech_location}')
        logger.debug(f'Server SID: {server_sid}')
        logger.debug(f'Game Mode: {game_mode}')
        logger.info(f'Short Game ID: {short_game_id}')
        logger.debug('---------------------------RAID DEBUG INFO END---------------------------')

    @logger.catch
    def get_last_raid_location(self) -> str | None:
        logger.info('Start searching for last raid info...')
        last_info = None
        with open(self.current_output_logs, 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if 'TRACE-NetworkGameCreate profileStatus' in line:
                    last_info = line
                    self.last_game_log_index = index
        if not last_info:
            logger.info('Last raid info not found!')
            return None
        logger.info(f'Last raid info found -> {last_info}, line index -> {index + 1}')
        raid_info = last_info.split(',')
        profile_uid_data = raid_info[0].split(' ')
        server_ip = raid_info[3].split(' ')[2]
        server_port = raid_info[4].split(' ')[2]
        self.last_game_server = f'{server_ip}:{server_port}'
        tech_location = raid_info[5].split(' ')[2]
        if settings.log_level.upper() == 'DEBUG':
            profile_uid = profile_uid_data[len(profile_uid_data) - 1]
            raid_mode = raid_info[2].split(' ')[2]
            server_sid = raid_info[6].split(' ')[2]
            game_mode = raid_info[7].split(' ')[2]
            short_game_id = raid_info[8].split(' ')[2].replace("'", '').replace('\n', '')
            self.__debug_raid_log(
                profile_uid=profile_uid,
                raid_mode=raid_mode,
                last_game_server=self.last_game_server,
                tech_location=tech_location,
                server_sid=server_sid,
                game_mode=game_mode,
                short_game_id=short_game_id,
            )
        logger.info(f'Last raid info was found!')
        location = self.__get_location_name(location_tech_name=tech_location, lang='ru')
        return location

# Disconnect (address: 84.17.53.68:1704307)

    def get_disconnect_message(self) -> bool:
        logger.info('Start searching for disconnect message...')
        if self.last_game_log_index and self.last_game_server:
            with open(self.current_output_logs, 'r') as file:
                lines = file.readlines()
                for index, line in enumerate(lines):
                    if f'Disconnect (address: {self.last_game_server})' in line and self.last_game_log_index < index:
                        logger.info(f'Last raid disconnect info found! -> {line}, line index -> {index + 1}')
                        return True
                logger.info(f'Last raid disconnect info was not found!')
                return False
        else:
            logger.info('Empty last game log or last game server')
            return False

    def add_new_player_in_group(self) -> None:
        logger.info('Start searching lobby info...')
        with open(self.current_output_logs, 'r', encoding='utf-8') as file:
            results = set()
            for line in file:
                if 'Nickname' in line and not 'SavageNickname' in line:
                    with_no_space = line.replace(' ', '')
                    with_no_test = with_no_space.replace('\n', '')
                    user_nickname = with_no_test.split(':')[1].replace(',', '').replace('"', '')
                    results.add(user_nickname)
        logger.debug(f'Users in lobby: {results}')
        logger.debug(f'current_player_name: {self.current_player_name}')
        user_len = len(results)
        if self.current_player_name == results:
            logger.info(f'No new player in lobby!')
            return
        self.current_player_count += user_len
        self.current_player_name = results
        logger.info(f'New lobby count -> {self.current_player_count}')
        logger.info(f'Updating lobby info!')

    # def delete_player_in_group(self) -> None:
    #     logger.info('Start searching lobby info for leaved users...')
    #     with open(self.current_output_logs, 'r', encoding='utf-8') as file:
    #         lines = file.readlines()
    #         for index, line in enumerate(lines):
    #             if '"type": "groupMatchUserLeave"' in line:
    #                 leaved_user = lines[index + 3]
    #                 logger.info(f'Leaved user -> {leaved_user}')
    #                 self.current_player_name.remove(leaved_user)
    #                 self.current_player_count -= 1
    #                 logger.info(f'New user count -> {self.current_player_count}')


log_analyzer = LogAnalyzer()
