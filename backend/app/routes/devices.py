from fastapi import APIRouter,HTTPException, Depends

from app.services.device_manager import device_manager
from app.schemas.device import DeviceState

from app.core.security import get_current_user
from app.models import User

router = APIRouter()


@router.get("")
def get_devices(
    user: User = Depends(get_current_user),
):

    return device_manager.get_devices()


@router.get("/{device_name}")
def get_device(
    device_name: str,
    user: User = Depends(get_current_user),
):

    device = device_manager.get_device(device_name)

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return device


@router.post("/{device_name}/on")
def turn_on(
    device_name: str,
    user: User = Depends(get_current_user),
):

    device_manager.turn_on(device_name)

    return {
        "message": "Device turned on",
    }


@router.post("/{device_name}/off")
def turn_off(
    device_name: str,
    user: User = Depends(get_current_user),
):

    device_manager.turn_off(device_name)

    return {
        "message": "Device turned off",
    }
    
@router.post("/{device_name}/state")
def set_state(
    device_name: str,
    data: DeviceState,
    user: User = Depends(get_current_user),
):

    device = device_manager.set_state(
        device_name,
        data.state.upper(),
    )

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return {
        "success": True,
    }


@router.post("/{device_name}/toggle")
def toggle_state(
    device_name: str,
    user: User = Depends(get_current_user),
):

    device = device_manager.toggle_state(device_name)

    if device is None:
        raise HTTPException(
            status_code=404,
            detail="Device not found",
        )

    return {
        "success": True,
    }