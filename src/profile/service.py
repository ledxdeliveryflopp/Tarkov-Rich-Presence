import httpx
from loguru import logger

from src.const import const
from src.profile.schemas import ProfileSchemas
from src.settings import settings


class ProfileGrabber:

    def __init__(self):
        ...

    # TODO: Вынести URL
    @logger.catch
    def grab_user_profile(self) -> ProfileSchemas | None:
        logger.info('Getting user profile info...')
        logger.debug(f'Getting user profile info for user -> {settings.user_uid}')
        if not settings.user_uid:
            logger.warning(f'No stored user uid found, skipping grab profile info!')
            return None
        url = f'https://players.tarkov.dev/profile/{settings.user_uid}.json'
        response = httpx.get(url=url)
        if response.status_code != httpx.codes.OK:
            logger.error('Failed to get user profile info!')
            logger.debug(f'Response code -> {response.status_code}')
            logger.debug(f'Response text -> {response.text}')
            logger.debug(f'Response json -> {response.json()}')
            return None
        response_data = response.json()
        validated_data = self.__validated_user_info(response_data=response_data)
        if not validated_data:
            logger.warning('User info validation failed!')
            logger.debug(f'User data -> {response_data}')
            return None
        logger.info('Getting user information is successful')
        return validated_data

    @logger.catch
    def __convert_exp_to_lvl(self, exp: float) -> int:
        logger.info('Start converting exp to lvl...')
        closest_key = min(const.levels.range.keys(), key=lambda x: abs(x - exp))
        logger.debug(f'Closest level -> {closest_key}')
        logger.info('Exp converted to lvl!')
        return const.levels.range[closest_key]

    @logger.catch
    def __validated_user_info(self, response_data: dict) -> ProfileSchemas | None:
        logger.info('Validating user profile info...')
        user_info = ProfileSchemas(**response_data)
        logger.info(f'User username -> {user_info.info.nickname}')
        logger.debug(f'User side -> {user_info.info.side}')
        logger.debug(f'User prestige -> {user_info.info.prestige_level}')
        logger.debug(f'User exp -> {user_info.info.experience}')
        user_level = self.__convert_exp_to_lvl(exp=user_info.info.experience)
        user_info.info.experience = user_level
        logger.debug(f'User level -> {user_level}')
        return user_info


http_grabber = ProfileGrabber()
