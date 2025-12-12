from typing import Literal

from loguru import logger

from src.settings import settings
import tracemalloc


class AnalyzerUtils:

    @staticmethod
    def profiler(func):
        def wrapper(*args, **kwargs):
            tracemalloc.start()
            try:
                result = func(*args, **kwargs)
                current, peak = tracemalloc.get_traced_memory()
                logger.debug(f'{func.__name__}, current bytes -> {current} | peak bytes -> {peak}')
                return result
            finally:
                tracemalloc.stop()
        return wrapper


    @staticmethod
    @logger.catch
    def get_location_name(location_tech_name: str, lang: Literal['ru', 'en']) -> str:
        logger.debug(f'Get location -> {location_tech_name}, lang -> {lang}')
        logger.info('Get location name...')
        formated_name = location_tech_name.replace(' ', '')
        location_block = settings.locations_data['locations'].get(formated_name, None)
        if not location_block:
            logger.debug(f'Location -> {location_tech_name} not found!')
            logger.info('Location not found!')
            return 'Unknown location'
        location = location_block[lang]
        logger.debug(f'Location -> {location} found!')
        logger.info('Location was found!')
        return location

    @staticmethod
    @logger.catch
    def get_location_image(location_tech_name: str) -> str:
        logger.debug(f'Get location image -> {location_tech_name}...')
        logger.info('Get location image...')
        location_block = settings.locations_data['locations'].get(location_tech_name, None)
        if not location_block:
            logger.debug(f'Location image -> {location_tech_name} not found!')
            logger.info('Location image not found!')
            return 'Unknown location'
        location_image_status = location_block['image']['status']
        logger.debug(f'Location image status -> {location_image_status}')
        if location_image_status is False:
            logger.info('Location image not found!')
            return 'Unknown location'
        location_image = location_block['image']['code']
        logger.debug(f'Location image -> {location_image}')
        logger.info('Location image was found!')
        return location_image


analyzer_utils = AnalyzerUtils()
