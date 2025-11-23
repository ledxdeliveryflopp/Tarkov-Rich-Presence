# This is a sample Python script.
import json
import os
import time
from datetime import datetime
from typing import Literal

import yaml
from loguru import logger
from pypresence import Presence, ActivityType
from yaml import SafeLoader


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


class Service:

    def __init__(self):
        self.last_game_server = None
        self.main_log_dir = 'Logs'
        self.current_session_logs: str = None
        self.current_output_logs: str = None
        self.user_profile_uid: str = None
        self.current_server_address: str = None
        self.last_game_id: str = None
        self.current_player_count: int = 1
        self.current_player_name: list[str] = []

    def get_main_log_path(self) -> None:
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
        current_session_logs = os.listdir(f'{self.main_log_dir}/{last_dir_name}')
        game_log = [i for i in current_session_logs if 'application' in i]
        if len(game_log) == 0:
            print('empty log folder')
        self.current_session_logs = f'{self.main_log_dir}/{last_dir_name}/{game_log[0]}'
        logger.debug(f'Application log path: {self.current_session_logs}')

    def get_output_log_path(self) -> None:
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
        current_session_logs = os.listdir(f'{self.main_log_dir}/{last_dir_name}')
        game_log = [i for i in current_session_logs if 'output' in i]
        if len(game_log) == 0:
            print('empty log folder')
        self.current_output_logs = f'{self.main_log_dir}/{last_dir_name}/{game_log[0]}'
        logger.debug(f'Application output path: {self.current_output_logs}')

    @staticmethod
    def get_location_name(location_tech_name: str, lang: Literal['ru', 'en']) -> str:
        with open('locations.yml', encoding='utf-8') as locations_data:
            data = yaml.load(locations_data, Loader=SafeLoader)
            formated_name = location_tech_name.replace(' ', '')
            return data['locations'][formated_name][lang]

    def get_user_profile_uid(self) -> None:
        # SelectProfile
        # ProfileId:
        with open(self.current_output_logs, 'r') as f:
            data = f.readlines()
            for line in data:
                if 'SelectProfile ProfileId:' in line:
                    test = line.split(' ')
                    print(test[2].split(''))

    def check_user_create_game(self) -> str:
        last_info = None
        with open(self.current_output_logs, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'TRACE-NetworkGameCreate profileStatus' in line:
                    last_info = line
        splited_info = last_info.split(',')
        # logger.debug(f'splited_info: {splited_info}')
        profile_uid_data = splited_info[0].split(' ')
        profile_uid = profile_uid_data[len(profile_uid_data) - 1]
        logger.info(f'Profile ID: {profile_uid}')
        raid_mode = splited_info[2].split(' ')[2]
        logger.info(f'Raid Mode: {raid_mode}')
        server_ip = splited_info[3].split(' ')[2]
        server_port = splited_info[4].split(' ')[2]
        self.last_game_server = f'{server_ip}:{server_port}'
        logger.debug(f'Server IP:PORT: {self.last_game_server}')
        tech_location = splited_info[5].split(' ')[2]
        logger.debug(f'Tech Location: {tech_location}')
        location_from_yaml = self.get_location_name(tech_location, 'ru')
        logger.info(f'Location from yaml: {location_from_yaml}')
        server_sid = splited_info[6].split(' ')[2]
        logger.debug(f'Server SID: {server_sid}')
        game_mode = splited_info[7].split(' ')[2]
        logger.debug(f'Game Mode: {game_mode}')
        short_game_id = splited_info[8].split(' ')[2].replace("'", '').replace('\n', '')
        logger.info(f'Short Game ID: {short_game_id}')

    def get_disconnect_message(self) -> str:
        with open(self.current_output_logs, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if f'Disconnect (address: {self.last_game_server})' in line:
                    logger.debug(f'Disconnect line: {line}')
                    logger.debug('Disconnect message')

    def add_new_player_in_group(self) -> None:
        with open(self.current_output_logs, 'r', encoding='utf-8') as file:
            results = set()
            for line in file:
                if 'Nickname' in line and not 'SavageNickname' in line:
                    with_no_space = line.replace(' ', '')
                    with_no_test = with_no_space.replace('\n', '')
                    user_nickname = with_no_test.split(':')[1].replace(',', '').replace('"', '')
                    results.add(user_nickname)
        logger.info(f'users in group: {results}')
        self.current_player_count += len(results)
        logger.info(f'New lobby count: {self.current_player_count}')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test = Service()
    logger.info('----------------------------------Поиск-логов----------------------------------')
    test.get_main_log_path()
    test.get_output_log_path()
    logger.info('----------------------------------Информация-о-рейде----------------------------------')
    test.check_user_create_game()
    logger.info('----------------------------------Игроки-в-группе----------------------------------')
    test.add_new_player_in_group()
    logger.info('----------------------------------Отключение-от-cервера----------------------------------')
    test.get_disconnect_message()
    # while True:
    #     test.add_new_player_in_group()
    #     location = test.get_current_location()
    #     client_id = "1441056758645915698"
    #     RPC = Presence(client_id)
    #     RPC.connect()
    #     RPC.update(
    #         activity_type=ActivityType.PLAYING,
    #         details='В Рейде',
    #         state=f'Локация: {location}',
    #         party_size=[test.current_player_count, 5],
    #     )
    #     time.sleep(15)

# 2025-11-20 15:40:04.216|1.0.0.1.41837|Info|application|[Transit] `5e074854fbf4d207112e6a3e` Count:0, EventPlayer:False

# предположительно выход

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# TODO: проверка в рейде/нет по отключению от сервера + проверка что найденный в логе рейд