from typing import Literal

from pydantic import BaseModel


class CoreLevel(BaseModel):

    profiler: bool
    log_folder_path: str
    deque_search: bool
    deque_max_depth: int


class PresenceLevel(BaseModel):
    refresh_time: int
    timer_mode: Literal['divided', 'general']
    show_zero_prestige: bool


class MainSettingsLevel(BaseModel):

    language: Literal['ru', 'en']
    presence: PresenceLevel
    core: CoreLevel


class SettingsSchemas(BaseModel):

    settings: MainSettingsLevel
