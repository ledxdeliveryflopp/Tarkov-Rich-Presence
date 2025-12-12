from typing import Optional

from pydantic import BaseModel, Field


class ProfileInfo(BaseModel):

    nickname: str
    side: str
    prestige_level: Optional[int] = Field(None, alias='prestigeLevel')
    experience: int | float


class ProfileSchemas(BaseModel):

    info: ProfileInfo
    updated: float | int
