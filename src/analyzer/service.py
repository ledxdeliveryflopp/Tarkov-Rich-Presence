import time
from typing import Literal, Any

from loguru import logger

from src.analyzer.utils import analyzer_utils
from src.const import const
from src.settings import settings
from src.storage import storage


class LogAnalyzer:

    def __init__(self):
        self.last_game_server: str | None = None
        self.current_player_count: int = 0
        self.current_player_name: set[str] = set()
        self.last_game_log_index: int | None = None
        self.game_ignores_indexes: set = set()
        self.disconnect_ignores_indexes: set = set()
        self.last_game_log_finish_index: int | None = None
        self.log_file_data: Any = None
        self.last_game_uid = None

    @logger.catch
    def __open_log_file(self):
        logger.debug('Open log file...')
        try:
            logger.debug('Open file with cp1251 encoding')
            with open(settings.game_output_log_path, 'r', encoding='cp1251') as file:
                self.log_file_data = file.readlines()
                logger.debug('File successfully opened')
        except UnicodeDecodeError:
            logger.warning('UnicodeDecodeError while open log file with cp1251 encoding!')
            logger.debug('Open file with utf-8 encoding')
            with open(settings.game_output_log_path, 'r', encoding='utf-8', errors='replace') as file:
                self.log_file_data = file.readlines()
                logger.debug('File successfully opened')

    @logger.catch
    def get_user_id(self):
        self.__open_log_file()
        logger.info('Get user uid...')
        lines = self.log_file_data
        for index, line in enumerate(lines):
            if 'application|SelectProfile' in line:
                logger.debug(f'Select profile info -> {line}, index -> {index}')
                user_uid = line.split(':')[-1].strip()
                logger.debug(f'Select profile uid -> {user_uid}')
                logger.info(f'User profile uid found!')
                settings.store_user_id(user_id=user_uid)
        logger.info(f'User profile uid dont found!')

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
        logger.debug(f'Profile ID -> {profile_uid}')
        logger.debug(f'Raid Mode -> {raid_mode}')
        logger.debug(f'Server IP:PORT -> {last_game_server}')
        logger.debug(f'Tech Location -> {tech_location}')
        logger.debug(f'Server SID -> {server_sid}')
        logger.debug(f'Game Mode -> {game_mode}')
        logger.debug(f'Short Game ID -> {short_game_id}')
        logger.debug('---------------------------RAID DEBUG INFO END---------------------------')

    @logger.catch
    def __build_pvp_info(self, raid_info: list) -> (str, str):
        profile_uid_data = raid_info[0].split(' ')
        server_ip = raid_info[3].split(' ')[2]
        server_port = raid_info[4].split(' ')[2]
        self.last_game_server = f'{server_ip}:{server_port}'
        tech_location = raid_info[5].split(' ')[2].lower()
        return profile_uid_data, tech_location

    @logger.catch
    def __build_pve_info(self, raid_info: list, info_type) -> (str, str):
        logger.info(f'Pve raid info type -> {info_type}')
        if info_type == 'pvp_type':
            tech_location = raid_info[3].split(':')[1].split(' ')[0].lower()
            raid_uid = raid_info[8].split(' ')[2].replace("'", '').lower()
            logger.info(f'Pve raid pvp info type uid -> {raid_uid}')
            logger.info(f'Pve raid pvp info type location -> {tech_location}')
            return tech_location, raid_uid
        splited_info = raid_info[3].split(':')[1].replace('\n', '').strip().split('->')
        locations = [s.strip() for s in splited_info if s.strip()]
        tech_location = locations[-1:][0].lower()
        raid_uid = raid_info[1].split(':')[1]
        logger.info(f'Pve raid pve info uid -> {raid_uid}')
        logger.info(f'Pve raid pve info location -> {tech_location}')
        return tech_location, raid_uid

    def get_pve_info(self, lines: list[str]) -> (str, str):
        last_pve_index = 0
        last_pvp_index = 0
        last_pvp_info = None
        last_pve_info = None
        for index, line in enumerate(lines):
            if '[Transit] Flag:Common' in line:
                last_pve_info = line
                last_pve_index = index
            elif 'TRACE-NetworkGameCreate profileStatus' in line:
                last_pvp_info = line
                last_pvp_index = index
        logger.debug(f'Last pve info -> {last_pve_info}')
        logger.debug(f'Last pvp info -> {last_pvp_info}')
        logger.debug(f'Last pve index -> {last_pve_index}')
        logger.debug(f'Last pvp index -> {last_pvp_index}')
        if last_pve_index > last_pvp_index:
            self.last_game_log_index = last_pve_index
            logger.debug(f'last pve index > last pvp index')
            return last_pve_info, 'pve_type'
        else:
            logger.debug(f'last pve index < last pvp index')
            self.last_game_log_index = last_pvp_index
            return last_pvp_info, 'pvp_type'

    def get_pvp_info(self, lines: list[str]):
        last_info = None
        for index, line in enumerate(lines):
            if 'TRACE-NetworkGameCreate profileStatus' in line:
                last_info = line
                self.last_game_log_index = index
        return last_info

    @logger.catch
    def get_last_raid_location(self) -> (str, str) or None:
        self.__open_log_file()
        self.__get_game_mode()
        logger.info('Start searching for last raid info...')
        last_info = None
        lines = self.log_file_data
        if settings.game_mode == 'pve':
            last_info, info_type = self.get_pve_info(lines=lines)
        elif settings.game_mode == 'regular':
            last_info = self.get_pvp_info(lines=lines)
        if not last_info:
            logger.info('Last raid info not found!')
            return None, None
        logger.debug(f'Last raid info found -> {last_info}, line index -> {self.last_game_log_index + 1}')
        raid_info = last_info.split(',')
        if settings.game_mode == 'regular':
            profile_uid_data, tech_location = self.__build_pvp_info(raid_info=raid_info)
        elif settings.game_mode == 'pve':
            tech_location, raid_uid = self.__build_pve_info(raid_info=raid_info, info_type=info_type)
            if not tech_location or not raid_uid:
                profile_uid_data, tech_location = self.__build_pvp_info(raid_info=raid_info)
            if not self.last_game_uid and raid_uid:
                logger.debug(f'Save raid id -> {raid_uid}')
                self.last_game_uid = raid_uid
            elif self.last_game_uid and raid_uid != self.last_game_uid:
                logger.debug('This raid have another id!')
                logger.debug(f'Actual Game id -> {raid_uid}, last game id -> {self.last_game_uid}')
                storage.start_raid_time = time.time()
                self.last_game_uid = raid_uid
                logger.debug(f'Set new presence time -> {storage.start_raid_time}')
        else:
            return None, None
        if settings.log_level.upper() == 'DEBUG' and settings.game_mode == 'pvp':
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
        logger.info(f'Last raid info found!')
        location = analyzer_utils.get_location_name(location_tech_name=tech_location, lang=settings.language)
        location_image = analyzer_utils.get_location_image(location_tech_name=tech_location)
        return location, location_image

    def __get_game_mode(self) -> None:
        logger.info('Get game mode...')
        lines = self.log_file_data
        for index, line in enumerate(lines):
            if 'application|Session mode:' in line:
                session_info = line.split(':')[-1].strip().lower()
                settings.game_mode = session_info
                # logger.debug(f'Game mode info -> {line}, line index -> {index + 1}')
        logger.debug(f'Game mode -> {settings.game_mode}')
        settings.readable_game_mode = const.modes.game_modes.get(settings.game_mode, settings.game_mode)
        logger.info(f'Readable game mode -> {settings.readable_game_mode}')


    @logger.catch
    def get_disconnect_message(self) -> bool:
        logger.info('Start searching for disconnect message...')
        if self.last_game_log_index and self.last_game_server:
            lines = self.log_file_data
            for index, line in enumerate(lines):
                if f'Disconnect (address: {self.last_game_server})' in line and self.last_game_log_index < index:
                    logger.debug(f'Last raid disconnect info found! -> {line}, line index -> {index + 1}')
                    logger.info('Last raid disconnect info found!')
                    return True
            logger.info('Last raid disconnect info was not found!')
            return False
        else:
            logger.info('Empty last game log or last game server')
            return False

    # TODO: нужен более надежный способ
    @logger.catch
    def update_group_count(self) -> None:
        logger.info('Start searching lobby info...')
        lobby_results = set()
        lines = self.log_file_data
        for index, line in enumerate(lines):
            if 'Got notification | GroupMatchRaidReady' in line:
                user_nickname = lines[index + 8].strip()
                fixed = user_nickname.split(' ')[1].replace(',', '').replace('"', '')
                logger.debug(f'User join to lobby found! -> {line}, line index -> {index + 1}')
                check_result = self.check_user_for_leave(user=fixed, connect_user_line=index)
                logger.debug(f'Check result -> {check_result}')
                if check_result is False:
                    lobby_results.add(user_nickname)
        logger.debug(f'Users in lobby(log) -> {lobby_results}')
        logger.debug(f'Stored lobby players -> {self.current_player_name}')
        user_len = len(lobby_results)
        self.current_player_count = user_len + 1
        self.current_player_name = lobby_results
        logger.debug(f'New lobby count -> {self.current_player_count}')
        logger.info(f'Updating lobby info!')

    @logger.catch
    def check_user_for_leave(self, user: str, connect_user_line: int) -> bool:
        logger.info('Start searching lobby info for leaved users...')
        lines = self.log_file_data
        for index, line in enumerate(lines):
            if '"type": "groupMatchUserLeave"' in line:
                username_index = index + 3
                leaved_user = lines[username_index].strip().split(' ')[1].replace('"', '')
                logger.debug(f'Check user leave -> {user}, index -> {connect_user_line}')
                logger.debug(f'Finded user leave -> {leaved_user}, index -> {username_index}')
                if leaved_user == user and username_index >= connect_user_line:
                    logger.debug(f'Group match user leave found! -> {line}, line index -> {username_index}')
                    logger.debug(f'Leaved user -> {leaved_user}')
                    logger.info('Ignored user was found!')
                    return True
        return False


log_analyzer = LogAnalyzer()
