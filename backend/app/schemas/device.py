from sqlmodel import SQLModel


class DeviceState(SQLModel):
    state: str
    
class DeviceBrightness(SQLModel):
    brightness: int

class DeviceColor(SQLModel):
    color: str

class DevicePosition(SQLModel):
    position: int