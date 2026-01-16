from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

import config as config_module
from app.db.models import AppSetting


@dataclass(frozen=True)
class SettingDefinition:
    key: str
    value_type: str
    requires_restart: bool = False
    env_delimiter: str = ","
    allowed_values: tuple[str, ...] | None = None


SETTINGS = [
    SettingDefinition("NOTIFY_STATUS_CHANGE", "bool"),
    SettingDefinition("NOTIFY_USER_CREATED", "bool"),
    SettingDefinition("NOTIFY_USER_UPDATED", "bool"),
    SettingDefinition("NOTIFY_USER_DELETED", "bool"),
    SettingDefinition("NOTIFY_USER_DATA_USED_RESET", "bool"),
    SettingDefinition("NOTIFY_USER_SUB_REVOKED", "bool"),
    SettingDefinition("NOTIFY_IF_DATA_USAGE_PERCENT_REACHED", "bool"),
    SettingDefinition("NOTIFY_IF_DAYS_LEFT_REACHED", "bool"),
    SettingDefinition("NOTIFY_LOGIN", "bool"),
    SettingDefinition("NOTIFY_REACHED_USAGE_PERCENT", "list[int]"),
    SettingDefinition("NOTIFY_DAYS_LEFT", "list[int]"),
    SettingDefinition("RECURRENT_NOTIFICATIONS_TIMEOUT", "int"),
    SettingDefinition("NUMBER_OF_RECURRENT_NOTIFICATIONS", "int"),
    SettingDefinition("ACTIVE_STATUS_TEXT", "str"),
    SettingDefinition("EXPIRED_STATUS_TEXT", "str"),
    SettingDefinition("LIMITED_STATUS_TEXT", "str"),
    SettingDefinition("DISABLED_STATUS_TEXT", "str"),
    SettingDefinition("ONHOLD_STATUS_TEXT", "str"),
    SettingDefinition("USERS_AUTODELETE_DAYS", "int"),
    SettingDefinition("USER_AUTODELETE_INCLUDE_LIMITED_ACCOUNTS", "bool"),
    SettingDefinition("WEBHOOK_ADDRESS", "list[str]"),
    SettingDefinition("DISCORD_WEBHOOK_URL", "str"),
    SettingDefinition("SUB_UPDATE_INTERVAL", "str"),
    SettingDefinition("SUB_SUPPORT_URL", "str"),
    SettingDefinition("SUB_PROFILE_TITLE", "str"),
    SettingDefinition(
        "SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS",
        "bool",
    ),
    SettingDefinition(
        "SUBSCRIPTION_CUSTOM_NOTES_EXPIRED",
        "list[str]",
        env_delimiter="|",
    ),
    SettingDefinition(
        "SUBSCRIPTION_CUSTOM_NOTES_LIMITED",
        "list[str]",
        env_delimiter="|",
    ),
    SettingDefinition(
        "SUBSCRIPTION_CUSTOM_NOTES_DISABLED",
        "list[str]",
        env_delimiter="|",
    ),
    SettingDefinition(
        "HWID_DEVICE_LIMIT_ENABLED",
        "str",
        allowed_values=("enabled", "disabled", "logging"),
    ),
    SettingDefinition("HWID_FALLBACK_DEVICE_LIMIT", "int"),
    SettingDefinition("HWID_DEVICE_RETENTION_DAYS", "int"),
    SettingDefinition("JOB_CORE_HEALTH_CHECK_INTERVAL", "int", requires_restart=True),
    SettingDefinition("JOB_RECORD_NODE_USAGES_INTERVAL", "int", requires_restart=True),
    SettingDefinition("JOB_RECORD_USER_USAGES_INTERVAL", "int", requires_restart=True),
    SettingDefinition("JOB_REVIEW_USERS_INTERVAL", "int", requires_restart=True),
    SettingDefinition("JOB_SEND_NOTIFICATIONS_INTERVAL", "int", requires_restart=True),
    SettingDefinition(
        "JOB_RECORD_REALTIME_BANDWIDTH_INTERVAL", "int", requires_restart=True
    ),
    SettingDefinition("JOB_RECORD_USER_USAGES_WORKERS", "int", requires_restart=True),
    SettingDefinition("JOB_CORE_HEALTH_CHECK_MAX_INSTANCES", "int", requires_restart=True),
    SettingDefinition(
        "JOB_RECORD_USER_USAGES_MAX_INSTANCES", "int", requires_restart=True
    ),
    SettingDefinition(
        "JOB_RECORD_NODE_USAGES_MAX_INSTANCES", "int", requires_restart=True
    ),
    SettingDefinition(
        "JOB_RECORD_REALTIME_BANDWIDTH_MAX_INSTANCES", "int", requires_restart=True
    ),
    SettingDefinition("JOB_HWID_DEVICE_CLEANUP_INTERVAL", "int", requires_restart=True),
]

SETTINGS_BY_KEY = {setting.key: setting for setting in SETTINGS}


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on", "enabled"}:
            return True
        if normalized in {"false", "0", "no", "off", "disabled"}:
            return False
    raise ValueError("Invalid boolean value")


def _parse_list(value: Any, item_type: type, delimiter: str) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, str):
        raw_items = []
        for line in value.splitlines():
            raw_items.extend(line.split(delimiter))
        items = raw_items
    else:
        raise ValueError("Invalid list value")
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if item_type is int:
        return [int(item) for item in cleaned]
    return cleaned


def parse_setting_value(definition: SettingDefinition, value: Any) -> Any:
    if definition.value_type == "bool":
        return _parse_bool(value)
    if definition.value_type == "int":
        return int(value)
    if definition.value_type == "str":
        parsed = str(value) if value is not None else ""
        if definition.allowed_values and parsed not in definition.allowed_values:
            raise ValueError(
                f"Value must be one of {', '.join(definition.allowed_values)}"
            )
        return parsed
    if definition.value_type == "list[int]":
        return _parse_list(value, int, definition.env_delimiter)
    if definition.value_type == "list[str]":
        return _parse_list(value, str, definition.env_delimiter)
    raise ValueError("Unsupported setting type")


def format_env_value(definition: SettingDefinition, value: Any) -> str:
    if definition.value_type.startswith("list"):
        delimiter = f" {definition.env_delimiter} "
        return delimiter.join([str(item) for item in value])
    if definition.value_type == "bool":
        return "true" if value else "false"
    return str(value)


def _refresh_subscription_notes():
    config_module.SUBSCRIPTION_CUSTOM_NOTES = {
        "expired": config_module.SUBSCRIPTION_CUSTOM_NOTES_EXPIRED,
        "limited": config_module.SUBSCRIPTION_CUSTOM_NOTES_LIMITED,
        "disabled": config_module.SUBSCRIPTION_CUSTOM_NOTES_DISABLED,
    }


def get_db_settings(db: Session) -> dict[str, Any]:
    return {setting.key: setting.value for setting in db.query(AppSetting).all()}


def apply_db_overrides(db: Session) -> dict[str, Any]:
    applied = {}
    for key, raw_value in get_db_settings(db).items():
        definition = SETTINGS_BY_KEY.get(key)
        if not definition:
            continue
        parsed_value = parse_setting_value(definition, raw_value)
        setattr(config_module, key, parsed_value)
        if key.startswith("SUBSCRIPTION_CUSTOM_NOTES_"):
            _refresh_subscription_notes()
        applied[key] = parsed_value
    return applied


def upsert_db_settings(db: Session, values: dict[str, Any]) -> None:
    for key, value in values.items():
        setting = db.query(AppSetting).filter(AppSetting.key == key).first()
        if setting:
            setting.value = value
        else:
            db.add(AppSetting(key=key, value=value))
    db.commit()
