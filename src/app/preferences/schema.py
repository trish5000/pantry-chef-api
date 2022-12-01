from pydantic import BaseModel


class PreferencesBase(BaseModel):
    size_household: int


class PreferencesCreate(PreferencesBase):
    pass


class Preferences(PreferencesBase):
    pass
