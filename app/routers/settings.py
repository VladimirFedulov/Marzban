from typing import Any

from dotenv import set_key
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import config as config_module
from app import logger
from app.db import get_db
from app.models.admin import Admin
from app.settings import (
    SETTINGS,
    SETTINGS_BY_KEY,
    format_env_value,
    get_db_settings,
    parse_setting_value,
    refresh_v2ray_subscription_templates,
    upsert_db_settings,
)
from app.utils import responses

router = APIRouter(tags=["Settings"], prefix="/api", responses={401: responses._401})

ENV_PATH = config_module.ENV_PATH


class SettingsPayload(BaseModel):
    values: dict[str, Any]


@router.get(
    "/settings",
    responses={403: responses._403},
)
def get_settings(
    admin: Admin = Depends(Admin.check_sudo_admin),
    db: Session = Depends(get_db),
) -> dict:
    values: dict[str, Any] = {}
    metadata = {}
    db_values = get_db_settings(db)
    for setting in SETTINGS:
        if setting.key in db_values:
            values[setting.key] = db_values[setting.key]
        else:
            values[setting.key] = getattr(config_module, setting.key)
        metadata[setting.key] = {"requires_restart": setting.requires_restart}
    return {"values": values, "metadata": metadata}


@router.put(
    "/settings",
    responses={400: responses._400, 403: responses._403},
)
def update_settings(
    payload: SettingsPayload,
    admin: Admin = Depends(Admin.check_sudo_admin),
    db: Session = Depends(get_db),
) -> dict:
    can_write_env = True
    try:
        ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
        ENV_PATH.touch(exist_ok=True)
    except OSError as exc:
        logger.warning("Unable to prepare env file %s: %s", ENV_PATH, exc)
        can_write_env = False

    updated_values = {}
    for key, raw_value in payload.values.items():
        definition = SETTINGS_BY_KEY.get(key)
        if not definition:
            raise HTTPException(status_code=400, detail=f"Unknown setting: {key}")
        try:
            parsed_value = parse_setting_value(definition, raw_value)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        setattr(config_module, key, parsed_value)
        if key.startswith("SUBSCRIPTION_CUSTOM_NOTES_"):
            config_module.SUBSCRIPTION_CUSTOM_NOTES = {
                "expired": config_module.SUBSCRIPTION_CUSTOM_NOTES_EXPIRED,
                "limited": config_module.SUBSCRIPTION_CUSTOM_NOTES_LIMITED,
                "disabled": config_module.SUBSCRIPTION_CUSTOM_NOTES_DISABLED,
            }
        if key == "V2RAY_TEMPLATE_MAPPING":
            refresh_v2ray_subscription_templates()
        updated_values[key] = parsed_value

    upsert_db_settings(db, updated_values)

    if can_write_env:
        for key, parsed_value in updated_values.items():
            definition = SETTINGS_BY_KEY[key]
            try:
                set_key(str(ENV_PATH), key, format_env_value(definition, parsed_value))
            except OSError as exc:
                logger.warning("Unable to update env file %s: %s", ENV_PATH, exc)
                break
    return {"values": updated_values}
