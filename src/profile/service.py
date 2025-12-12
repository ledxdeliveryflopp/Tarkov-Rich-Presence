import asyncio
import bisect
import os
import time
from datetime import datetime
import httpx
from loguru import logger
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.constants import By

from src.const import const
from src.profile.schemas import ProfileSchemas
from src.settings import settings


class ProfileGrabber:

    def __init__(self):
        ...

    @staticmethod
    @logger.catch
    async def __update_profile() -> None:
        logger.info('Start updating profile in TarkovDev!')
        options = ChromiumOptions()
        options.headless = False
        options.binary_location = 'chrome-win64/chrome.exe'
        options.add_argument('--start-minimized')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--use-gl=swiftshader')
        options.add_argument('--disable-features=WebGLDraftExtensions')
        options.add_argument('--force-webrtc-ip-handling-policy=disable_non_proxied_udp')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--window-position=0,0')
        options.add_argument('--force-device-scale-factor=1')

        async with Chrome(options=options) as browser:
            tab = await browser.start()
            await tab.enable_auto_solve_cloudflare_captcha()
            if settings.game_mode == 'regular':
                async with tab.expect_and_bypass_cloudflare_captcha(
                        custom_selector=(By.ID, 'cf-turnstile'),
                        time_before_click=5,
                        time_to_wait_captcha=30,
                ):
                    await tab.go_to(f'https://tarkov.dev/players/regular/{settings.user_uid}')
            elif settings.game_mode == 'pve':
                async with tab.expect_and_bypass_cloudflare_captcha(
                        custom_selector=(By.ID, 'cf-turnstile'),
                        time_before_click=5,
                        time_to_wait_captcha=30,
                ):
                    await tab.go_to(f'https://tarkov.dev/players/pve/{settings.user_uid}')
            await asyncio.sleep(10)
            screenshot_path = os.path.join(os.getcwd(), 'pydoll_repo.png')
            await tab.take_screenshot(path=screenshot_path)
            title_bar = await tab.find(class_name='title-bar')
            if title_bar:
                title_text = await title_bar.text
                logger.debug(f'Title bar text -> {title_text}')
            else:
                logger.debug('Error while find title locator')
        logger.info('Finished updating profile in TarkovDev!')

    @staticmethod
    def __get_user_info() -> None or dict:
        if settings.game_mode == 'regular':
            url = f'https://players.tarkov.dev/profile/{settings.user_uid}.json'
        elif settings.game_mode == 'pve':
            url = f'https://players.tarkov.dev/pve/{settings.user_uid}.json'
        response = httpx.get(url=url)
        if response.status_code != httpx.codes.OK:
            logger.error('Failed to get user profile info!')
            logger.debug(f'Response code -> {response.status_code}')
            logger.debug(f'Response text -> {response.text}')
            logger.debug(f'Response json -> {response.json()}')
            return None
        response_data: dict = response.json()
        return response_data

    # TODO: Вынести URL
    @logger.catch
    def grab_user_profile(self) -> ProfileSchemas | None:
        logger.info('Getting user profile info...')
        logger.debug(f'Getting user profile info for user -> {settings.user_uid}')
        if not settings.user_uid:
            logger.warning(f'No stored user uid found, skipping grab profile info!')
            return None
        response_data = self.__get_user_info()
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
        logger.debug(f'Start converting exp -> {exp}')
        last_exp_values = [(entry['full_exp'], key) for key, entry in const.levels.range.items()]
        last_exp_values.sort()
        index = bisect.bisect_right(last_exp_values, (exp, float('inf')))
        closest_key = last_exp_values[index - 1][1] if index > 0 else None
        logger.debug(f'Closest level -> {closest_key}')
        logger.info('Exp converted to lvl!')
        return closest_key

    @logger.catch
    def __check_update_time(self, update_time: float) -> None:
        logger.info('Start checking user update time...')
        current_datetime = datetime.now()
        two_days_in_timestamp = 172800
        compare_timestamp = (current_datetime.timestamp() - two_days_in_timestamp) * 1000
        if update_time < compare_timestamp:
            logger.warning('User information is 2+ days out of date!')
            logger.debug(f'User update time -> {update_time}, current timestamp -> {compare_timestamp}')
            asyncio.run(self.__update_profile())
            return None
        logger.info('User update time check successful, update time less 2 day!')

    @logger.catch
    def __validated_user_info(self, response_data: dict) -> ProfileSchemas | None:
        logger.info('Validating user profile info...')
        user_info = ProfileSchemas(**response_data)
        self.__check_update_time(update_time=user_info.updated)
        user_level = self.__convert_exp_to_lvl(exp=user_info.info.experience)
        user_info.info.experience = user_level
        logger.debug(f'User info -> {user_info}')
        logger.info('Validating user profile info is successful!')
        return user_info


http_grabber = ProfileGrabber()
