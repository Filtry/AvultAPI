from pydantic import BaseModel, validator, Field
from typing import Union, Optional
from enums import *

class SortSettings(BaseModel):
    scenes: Optional[ScenesSort] = Field(default=None, description="Sorting criteria for scenes")
    gender: Optional[GenderSort] = Field(default=None, description="Sorting criteria for gender")
    actors: Optional[ActorsSort] = Field(default=None, description="Sorting criteria for actors")
    movies: Optional[ScenesSort] = Field(default=None, description="Sorting criteria for movies")
    series: Optional[ScenesSort] = Field(default=None, description="Sorting criteria for series")

# Pydantic model for the main settings
class SettingsModel(BaseModel):
    blur_img: Optional[bool] = Field(default=False, description="Enable or disable image blur")
    isDark: Optional[bool] = Field(default=False, description="Enable or disable dark mode")
    limit: Optional[int] = Field(default=None, description="Set the result limit")
    sort: Optional[SortSettings] = Field(default=None, description="Sort settings")

    @validator("blur_img", "isDark", pre=True, always=True)
    def parse_boolean(cls, value):
        if value == "on":
            return True
        return False

