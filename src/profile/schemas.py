from pydantic import BaseModel, Field


class ProfileInfo(BaseModel):

    nickname: str
    side: str
    prestige_level: int = Field(alias='prestigeLevel')
    experience: int | float


class ProfileSchemas(BaseModel):

    info: ProfileInfo
    updated: float | int
