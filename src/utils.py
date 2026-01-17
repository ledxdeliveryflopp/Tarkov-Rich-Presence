from typing import Iterator

import psutil
from loguru import logger

from src.const import const


@logger.catch
def find_eft_process() -> bool:
    logger.debug('Start finding EFT process')
    processes: Iterator[psutil.Process] = psutil.process_iter()
    for proc in processes:
        try:
            info = proc.as_dict(attrs=['pid', 'name', 'status'])
            proc_name = info['name']
            proc_status = info['status']
            if proc_name == const.proc.game_proc_name and proc_status == 'running':
                logger.debug(f'PID -> {proc_name}, Name -> {info['name']}, Status -> {proc_status}')
                return True
            else:
                continue
        except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
            logger.warning(exc)
            if proc_name is not None and proc_name == const.proc.game_proc_name:
                return False
            else:
                continue
