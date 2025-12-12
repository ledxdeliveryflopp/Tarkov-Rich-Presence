import time
from collections import deque
from itertools import islice
from typing import List

from loguru import logger

from src.analyzer.utils import analyzer_utils
from src.settings import settings
from src.storage import storage
from src.utils import calculate_time


class DequeService:

    @logger.catch
    def __open_log_file(self, line_count: int) -> deque[str]:
        logger.debug('Open log file...')
        try:
            logger.debug('Open file in utf-8')
            with open(settings.game_output_log_path, 'r', encoding='utf-8') as file:
                lines = deque(file, maxlen=line_count)
                return lines
        except UnicodeDecodeError:
            logger.debug('Open file in cp1251')
            with open(settings.game_output_log_path, 'r', encoding='cp1251', errors='replace') as file:
                if settings.deque_search is True:
                    lines = deque(file, maxlen=line_count)
                    logger.debug(f'File successfully opened with count -> {line_count}')
                    return lines

    @logger.catch
    @analyzer_utils.profiler
    def get_user_id(self, debug: bool):
        logger.info('Get user uid...')
        line_count = 10
        iter_count = 1
        while line_count < settings.deque_max_depth:
            lines = self.__open_log_file(line_count=line_count)
            for index, line in enumerate(lines):
                if 'application|SelectProfile' in line:
                    logger.debug(f'Select profile info -> {line}, index -> {index}')
                    user_uid = line.split(':')[-1].strip()
                    logger.debug(f'Select profile uid -> {user_uid}')
                    logger.info(f'User profile uid found!')
                    settings.store_user_id(user_id=user_uid)
                    return iter_count
            logger.debug(f'User uid not found with count -> {line_count}')
            line_count += 10
            logger.debug(f'Increasing line count to -> {line_count}')
            if debug is True:
                iter_count += 1
        logger.info(f'User profile uid dont found!')

    @logger.catch
    @analyzer_utils.profiler
    def __build_pvp_info(self, raid_info: list) -> (str, str):
        profile_uid_data = raid_info[0].split(' ')
        server_ip = raid_info[3].split(' ')[2]
        server_port = raid_info[4].split(' ')[2]
        self.last_game_server = f'{server_ip}:{server_port}'
        tech_location = raid_info[5].split(' ')[2].lower()
        return profile_uid_data, tech_location

    @logger.catch
    def __build_pve_info(self, raid_info: list) -> (str, str):
        tech_location = raid_info[3].split(':')[1].split(' ')[0].lower()
        raid_uid = raid_info[1].split(':')[1]
        return tech_location, raid_uid

    def open_slice_file(self, line_count: int) -> list[str]:
        with open(settings.game_output_log_path, 'r', encoding='utf-8') as file:
            return list(islice(file, line_count))

    @logger.catch
    @analyzer_utils.profiler
    def __get_game_mode(self) -> None:
        logger.info('Get game mode...')
        line_count = 10
        while line_count < settings.deque_max_depth:
            lines = self.open_slice_file(line_count=line_count)
            for index, line in enumerate(lines):
                if 'application|Session mode:' in line:
                    session_info = line.split(':')[-1].strip().lower()
                    settings.game_mode = session_info
                    logger.debug(f'Game mode info -> {line}, line index -> {index + 1}')
                    logger.debug(f'Game mode -> {settings.game_mode}')
                    return
            line_count += 10

    @analyzer_utils.profiler
    def get_game_info(self):
        last_info = None
        line_count = 10
        while line_count < settings.deque_max_depth:
            lines = self.__open_log_file(line_count=line_count)
            for index, line in enumerate(lines):
                if settings.game_mode == 'pve':
                    if '[Transit] Flag:Common' in line:
                        last_info = line
                        logger.debug(f'Last raid info found -> {last_info}, line index -> {index + 1}')
                        return last_info
                elif settings.game_mode == 'regular':
                    if 'TRACE-NetworkGameCreate profileStatus' in line:
                        last_info = line
                        logger.debug(f'Last raid info found -> {last_info}, line index -> {index + 1}')
                        return last_info
            line_count += 10
        if not last_info:
            logger.info('Last raid info not found!')
            return None, None

    @logger.catch
    @analyzer_utils.profiler
    def get_last_raid_location(self) -> (str, str) or None:
        logger.info('Start searching for last raid info...')
        self.__get_game_mode()
        last_info = self.get_game_info()
        raid_info = last_info.split(',')
        if settings.game_mode == 'regular':
            profile_uid_data, tech_location = self.__build_pvp_info(raid_info=raid_info)
        elif settings.game_mode == 'pve':
            tech_location, raid_uid = self.__build_pve_info(raid_info=raid_info)
            if not self.last_game_uid:
                logger.debug(f'Save raid id -> {raid_uid}')
                self.last_game_uid = raid_uid
            if self.last_game_uid and raid_uid != self.last_game_uid:
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


deque_service = DequeService()
