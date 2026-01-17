import json
import os
import re
from pathlib import Path

from decouple import config
from dotenv import load_dotenv

DEFAULT_ENV_PATH = Path(".env")
HOST_ENV_DIR = Path("/opt/marzban")

env_override = os.environ.get("MARZBAN_ENV_PATH")
if env_override:
    ENV_PATH = Path(env_override)
elif HOST_ENV_DIR.is_dir():
    ENV_PATH = HOST_ENV_DIR / ".env"
else:
    ENV_PATH = DEFAULT_ENV_PATH

load_dotenv(ENV_PATH)


SQLALCHEMY_DATABASE_URL = config("SQLALCHEMY_DATABASE_URL", default="sqlite:///db.sqlite3")
SQLALCHEMY_POOL_SIZE = config("SQLALCHEMY_POOL_SIZE", cast=int, default=10)
SQLIALCHEMY_MAX_OVERFLOW = config("SQLIALCHEMY_MAX_OVERFLOW", cast=int, default=30)

UVICORN_HOST = config("UVICORN_HOST", default="0.0.0.0")
UVICORN_PORT = config("UVICORN_PORT", cast=int, default=8000)
UVICORN_UDS = config("UVICORN_UDS", default=None)
UVICORN_SSL_CERTFILE = config("UVICORN_SSL_CERTFILE", default=None)
UVICORN_SSL_KEYFILE = config("UVICORN_SSL_KEYFILE", default=None)
UVICORN_SSL_CA_TYPE = config("UVICORN_SSL_CA_TYPE", default="public").lower()
DASHBOARD_PATH = config("DASHBOARD_PATH", default="/dashboard/")

DEBUG = config("DEBUG", default=False, cast=bool)
DOCS = config("DOCS", default=False, cast=bool)

ALLOWED_ORIGINS = config("ALLOWED_ORIGINS", default="*").split(",")

VITE_BASE_API = (
    f"{'https' if UVICORN_SSL_CERTFILE and UVICORN_SSL_KEYFILE else 'http'}://127.0.0.1:{UVICORN_PORT}/api/"
    if DEBUG and config("VITE_BASE_API", default="/api/") == "/api/"
    else config("VITE_BASE_API", default="/api/")
)

XRAY_JSON = config("XRAY_JSON", default="./xray_config.json")
XRAY_FALLBACKS_INBOUND_TAG = config("XRAY_FALLBACKS_INBOUND_TAG", cast=str, default="") or config(
    "XRAY_FALLBACK_INBOUND_TAG", cast=str, default=""
)
XRAY_EXECUTABLE_PATH = config("XRAY_EXECUTABLE_PATH", default="/usr/local/bin/xray")
XRAY_ASSETS_PATH = config("XRAY_ASSETS_PATH", default="/usr/local/share/xray")
XRAY_EXCLUDE_INBOUND_TAGS = config("XRAY_EXCLUDE_INBOUND_TAGS", default='').split()
XRAY_SUBSCRIPTION_URL_PREFIX = config("XRAY_SUBSCRIPTION_URL_PREFIX", default="").strip("/")
XRAY_SUBSCRIPTION_PATH = config("XRAY_SUBSCRIPTION_PATH", default="sub").strip("/")

TELEGRAM_API_TOKEN = config("TELEGRAM_API_TOKEN", default="")
TELEGRAM_ADMIN_ID = config(
    'TELEGRAM_ADMIN_ID',
    default="",
    cast=lambda v: [int(i) for i in filter(str.isdigit, (s.strip() for s in v.split(',')))]
)
TELEGRAM_PROXY_URL = config("TELEGRAM_PROXY_URL", default="")
TELEGRAM_LOGGER_CHANNEL_ID = config("TELEGRAM_LOGGER_CHANNEL_ID", cast=int, default=0)
TELEGRAM_LOGGER_TOPIC_ID = config("TELEGRAM_LOGGER_TOPIC_ID", cast=int, default=0)
TELEGRAM_DEFAULT_VLESS_FLOW = config("TELEGRAM_DEFAULT_VLESS_FLOW", default="")

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=1440)

CUSTOM_TEMPLATES_DIRECTORY = config("CUSTOM_TEMPLATES_DIRECTORY", default=None)
SUBSCRIPTION_PAGE_TEMPLATE = config("SUBSCRIPTION_PAGE_TEMPLATE", default="subscription/index.html")
HOME_PAGE_TEMPLATE = config("HOME_PAGE_TEMPLATE", default="home/index.html")
SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS = config(
    "SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS",
    default=False,
    cast=bool,
)

CLASH_SUBSCRIPTION_TEMPLATE = config("CLASH_SUBSCRIPTION_TEMPLATE", default="clash/default.yml")
CLASH_SETTINGS_TEMPLATE = config("CLASH_SETTINGS_TEMPLATE", default="clash/settings.yml")

SINGBOX_SUBSCRIPTION_TEMPLATE = config("SINGBOX_SUBSCRIPTION_TEMPLATE", default="singbox/default.json")
SINGBOX_SETTINGS_TEMPLATE = config("SINGBOX_SETTINGS_TEMPLATE", default="singbox/settings.json")

MUX_TEMPLATE = config("MUX_TEMPLATE", default="mux/default.json")

V2RAY_SUBSCRIPTION_TEMPLATE = config("V2RAY_SUBSCRIPTION_TEMPLATE", default="v2ray/default.json")
V2RAY_TEMPLATE_MAPPING = config("V2RAY_TEMPLATE_MAPPING", default="")
V2RAY_SUBSCRIPTION_TEMPLATES = {}
if V2RAY_TEMPLATE_MAPPING:
    try:
        V2RAY_SUBSCRIPTION_TEMPLATES = {
            k.strip(): v.strip()
            for k, v in (
                item.split(":") for item in V2RAY_TEMPLATE_MAPPING.split(",")
            )
        }
    except ValueError:
        pass
V2RAY_SETTINGS_TEMPLATE = config("V2RAY_SETTINGS_TEMPLATE", default="v2ray/settings.json")
V2RAY_META_CONFIG = config("V2RAY_META_CONFIG", default="v2ray/meta_config.json")

USER_AGENT_TEMPLATE = config("USER_AGENT_TEMPLATE", default="user_agent/default.json")
GRPC_USER_AGENT_TEMPLATE = config("GRPC_USER_AGENT_TEMPLATE", default="user_agent/grpc.json")

EXTERNAL_CONFIG = config("EXTERNAL_CONFIG", default="", cast=str)
LOGIN_NOTIFY_WHITE_LIST = [ip.strip() for ip in config("LOGIN_NOTIFY_WHITE_LIST",
                                                       default="", cast=str).split(",") if ip.strip()]

USE_CUSTOM_JSON_DEFAULT = config("USE_CUSTOM_JSON_DEFAULT", default=False, cast=bool)
USE_CUSTOM_JSON_FOR_V2RAYN = config("USE_CUSTOM_JSON_FOR_V2RAYN", default=False, cast=bool)
USE_CUSTOM_JSON_FOR_V2RAYNG = config("USE_CUSTOM_JSON_FOR_V2RAYNG", default=False, cast=bool)
USE_CUSTOM_JSON_FOR_STREISAND = config("USE_CUSTOM_JSON_FOR_STREISAND", default=False, cast=bool)
USE_CUSTOM_JSON_FOR_HAPP = config("USE_CUSTOM_JSON_FOR_HAPP", default=False, cast=bool)
USE_CUSTOM_JSON_FOR_NPVTUNNEL = config("USE_CUSTOM_JSON_FOR_NPVTUNNEL", default=False, cast=bool)

NOTIFY_STATUS_CHANGE = config("NOTIFY_STATUS_CHANGE", default=True, cast=bool)
NOTIFY_USER_CREATED = config("NOTIFY_USER_CREATED", default=True, cast=bool)
NOTIFY_USER_UPDATED = config("NOTIFY_USER_UPDATED", default=True, cast=bool)
NOTIFY_USER_DELETED = config("NOTIFY_USER_DELETED", default=True, cast=bool)
NOTIFY_USER_DATA_USED_RESET = config("NOTIFY_USER_DATA_USED_RESET", default=True, cast=bool)
NOTIFY_USER_SUB_REVOKED = config("NOTIFY_USER_SUB_REVOKED", default=True, cast=bool)
NOTIFY_IF_DATA_USAGE_PERCENT_REACHED = config("NOTIFY_IF_DATA_USAGE_PERCENT_REACHED", default=True, cast=bool)
NOTIFY_IF_DAYS_LEFT_REACHED = config("NOTIFY_IF_DAYS_LEFT_REACHED", default=True, cast=bool)
NOTIFY_LOGIN = config("NOTIFY_LOGIN", default=True, cast=bool)

ACTIVE_STATUS_TEXT = config("ACTIVE_STATUS_TEXT", default="Active")
EXPIRED_STATUS_TEXT = config("EXPIRED_STATUS_TEXT", default="Expired")
LIMITED_STATUS_TEXT = config("LIMITED_STATUS_TEXT", default="Limited")
DISABLED_STATUS_TEXT = config("DISABLED_STATUS_TEXT", default="Disabled")
ONHOLD_STATUS_TEXT = config("ONHOLD_STATUS_TEXT", default="On-Hold")

USERS_AUTODELETE_DAYS = config("USERS_AUTODELETE_DAYS", default=-1, cast=int)
USER_AUTODELETE_INCLUDE_LIMITED_ACCOUNTS = config("USER_AUTODELETE_INCLUDE_LIMITED_ACCOUNTS", default=False, cast=bool)


# USERNAME: PASSWORD
SUDOERS = {config("SUDO_USERNAME"): config("SUDO_PASSWORD")} \
    if config("SUDO_USERNAME", default='') and config("SUDO_PASSWORD", default='') \
    else {}


WEBHOOK_ADDRESS = config(
    'WEBHOOK_ADDRESS',
    default="",
    cast=lambda v: [address.strip() for address in v.split(',')] if v else []
)
WEBHOOK_SECRET = config("WEBHOOK_SECRET", default=None)

# recurrent notifications

# timeout between each retry of sending a notification in seconds
RECURRENT_NOTIFICATIONS_TIMEOUT = config("RECURRENT_NOTIFICATIONS_TIMEOUT", default=180, cast=int)
# how many times to try after ok response not recevied after sending a notifications
NUMBER_OF_RECURRENT_NOTIFICATIONS = config("NUMBER_OF_RECURRENT_NOTIFICATIONS", default=3, cast=int)

# sends a notification when the user uses this much of thier data
NOTIFY_REACHED_USAGE_PERCENT = config(
    "NOTIFY_REACHED_USAGE_PERCENT",
    default="80",
    cast=lambda v: [int(p.strip()) for p in v.split(',')] if v else []
)

# sends a notification when there is n days left of their service
NOTIFY_DAYS_LEFT = config(
    "NOTIFY_DAYS_LEFT",
    default="3",
    cast=lambda v: [int(d.strip()) for d in v.split(',')] if v else []
)

DISABLE_RECORDING_NODE_USAGE = config("DISABLE_RECORDING_NODE_USAGE", cast=bool, default=False)

# headers: profile-update-interval, support-url, profile-title
SUB_UPDATE_INTERVAL = config("SUB_UPDATE_INTERVAL", default="12")
SUB_SUPPORT_URL = config("SUB_SUPPORT_URL", default="https://t.me/")
SUB_PROFILE_TITLE = config("SUB_PROFILE_TITLE", default="Subscription")

def _parse_subscription_custom_headers(value):
    if value is None or value == "":
        return []
    if isinstance(value, list):
        entries = value
    elif isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        entries = parsed
    else:
        return []

    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).strip()
        header_value = str(entry.get("value", "")).strip()
        user_agent = str(entry.get("user_agent", "")).strip()
        if not name or not header_value:
            continue
        normalized.append(
            {"name": name, "value": header_value, "user_agent": user_agent}
        )
    return normalized

SUBSCRIPTION_CUSTOM_HEADERS = config(
    "SUBSCRIPTION_CUSTOM_HEADERS",
    default="",
    cast=_parse_subscription_custom_headers,
)


def _split_subscription_notes(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[|\n]", str(value))
    return [part.strip() for part in parts if part.strip()]


SUBSCRIPTION_CUSTOM_NOTES_EXPIRED = config(
    "SUBSCRIPTION_CUSTOM_NOTES_EXPIRED",
    default="",
    cast=_split_subscription_notes,
)
SUBSCRIPTION_CUSTOM_NOTES_LIMITED = config(
    "SUBSCRIPTION_CUSTOM_NOTES_LIMITED",
    default="",
    cast=_split_subscription_notes,
)
SUBSCRIPTION_CUSTOM_NOTES_DISABLED = config(
    "SUBSCRIPTION_CUSTOM_NOTES_DISABLED",
    default="",
    cast=_split_subscription_notes,
)
SUBSCRIPTION_CUSTOM_NOTES_HWID_LIMIT = config(
    "SUBSCRIPTION_CUSTOM_NOTES_HWID_LIMIT",
    default="",
    cast=_split_subscription_notes,
)
SUBSCRIPTION_CUSTOM_NOTES = {
    "expired": SUBSCRIPTION_CUSTOM_NOTES_EXPIRED,
    "limited": SUBSCRIPTION_CUSTOM_NOTES_LIMITED,
    "disabled": SUBSCRIPTION_CUSTOM_NOTES_DISABLED,
    "hwid_limit": SUBSCRIPTION_CUSTOM_NOTES_HWID_LIMIT,
}

# HWID device limit
def _cast_hwid_device_limit_mode(value):
    if value is None:
        return "disabled"
    if isinstance(value, bool):
        return "enabled" if value else "disabled"
    normalized = str(value).strip().lower()
    if normalized in {"enabled", "enable", "true", "1", "yes", "on"}:
        return "enabled"
    if normalized in {"disabled", "disable", "false", "0", "no", "off"}:
        return "disabled"
    if normalized in {"logging", "log"}:
        return "logging"
    raise ValueError(
        "HWID_DEVICE_LIMIT_ENABLED must be enabled/disabled/logging or a boolean-like value"
    )


HWID_DEVICE_LIMIT_ENABLED = config(
    "HWID_DEVICE_LIMIT_ENABLED", cast=_cast_hwid_device_limit_mode, default="disabled"
)
HWID_FALLBACK_DEVICE_LIMIT = config("HWID_FALLBACK_DEVICE_LIMIT", cast=int, default=1)
HWID_DEVICE_RETENTION_DAYS = config("HWID_DEVICE_RETENTION_DAYS", cast=int, default=-1)

# discord webhook log
DISCORD_WEBHOOK_URL = config("DISCORD_WEBHOOK_URL", default="")


# Interval jobs, all values are in seconds
JOB_CORE_HEALTH_CHECK_INTERVAL = config("JOB_CORE_HEALTH_CHECK_INTERVAL", cast=int, default=10)
JOB_RECORD_NODE_USAGES_INTERVAL = config("JOB_RECORD_NODE_USAGES_INTERVAL", cast=int, default=30)
JOB_RECORD_USER_USAGES_INTERVAL = config("JOB_RECORD_USER_USAGES_INTERVAL", cast=int, default=10)
JOB_REVIEW_USERS_INTERVAL = config("JOB_REVIEW_USERS_INTERVAL", cast=int, default=10)
JOB_SEND_NOTIFICATIONS_INTERVAL = config("JOB_SEND_NOTIFICATIONS_INTERVAL", cast=int, default=30)
JOB_RECORD_REALTIME_BANDWIDTH_INTERVAL = config("JOB_RECORD_REALTIME_BANDWIDTH_INTERVAL", cast=int, default=2)
JOB_RECORD_USER_USAGES_WORKERS = config("JOB_RECORD_USER_USAGES_WORKERS", cast=int, default=10)
JOB_CORE_HEALTH_CHECK_MAX_INSTANCES = config("JOB_CORE_HEALTH_CHECK_MAX_INSTANCES", cast=int, default=10)
JOB_RECORD_USER_USAGES_MAX_INSTANCES = config("JOB_RECORD_USER_USAGES_MAX_INSTANCES", cast=int, default=10)
JOB_RECORD_NODE_USAGES_MAX_INSTANCES = config("JOB_RECORD_NODE_USAGES_MAX_INSTANCES", cast=int, default=10)
JOB_RECORD_REALTIME_BANDWIDTH_MAX_INSTANCES = config(
    "JOB_RECORD_REALTIME_BANDWIDTH_MAX_INSTANCES",
    cast=int,
    default=1
)
JOB_HWID_DEVICE_CLEANUP_INTERVAL = config("JOB_HWID_DEVICE_CLEANUP_INTERVAL", cast=int, default=3600)
