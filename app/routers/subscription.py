import re
from threading import Lock
from datetime import datetime, timedelta
from distutils.version import LooseVersion
from time import time

from fastapi import APIRouter, Depends, Header, Path, Request, Response
from fastapi.responses import HTMLResponse

from sqlalchemy.exc import OperationalError

from app import logger
from app.db import Session, crud, get_db
from app.db.models import User
from app.dependencies import get_validated_sub, validate_dates
from app.models.user import SubscriptionUserResponse, UserResponse, get_next_reset_info
from app.subscription.share import (
    encode_title,
    format_subscription_profile_title,
    generate_fake_subscription,
    generate_subscription,
    get_hwid_limit_notes,
)
import config as config_module
from app.templates import render_template

client_config = {
    "clash-meta": {"config_format": "clash-meta", "media_type": "text/yaml", "as_base64": False, "reverse": False},
    "sing-box": {"config_format": "sing-box", "media_type": "application/json", "as_base64": False, "reverse": False},
    "clash": {"config_format": "clash", "media_type": "text/yaml", "as_base64": False, "reverse": False},
    "v2ray": {"config_format": "v2ray", "media_type": "text/plain", "as_base64": True, "reverse": False},
    "outline": {"config_format": "outline", "media_type": "application/json", "as_base64": False, "reverse": False},
    "v2ray-json": {"config_format": "v2ray-json", "media_type": "application/json", "as_base64": False,
                   "reverse": False}
}

router = APIRouter(tags=['Subscription'], prefix=f'/{config_module.XRAY_SUBSCRIPTION_PATH}')
_SUBSCRIPTION_CACHE: dict[tuple, dict[str, object]] = {}
_SUBSCRIPTION_CACHE_LOCK = Lock()
_SUBSCRIPTION_CACHE_TTL_SECONDS = 60
_SUBSCRIPTION_METADATA_UPDATE_SECONDS = 60
def _build_subscription_cache_key(
    user: UserResponse,
    config_format: str,
    as_base64: bool,
    reverse: bool,
) -> tuple:
    return (
        user.username,
        config_format,
        as_base64,
        reverse,
        user.used_traffic,
        user.data_limit,
        user.expire,
        user.status,
        user.on_hold_expire_duration,
    )


def _get_cached_subscription(cache_key: tuple) -> str | None:
    with _SUBSCRIPTION_CACHE_LOCK:
        cached = _SUBSCRIPTION_CACHE.get(cache_key)
        if not cached:
            return None
        if cached["expires_at"] < time():
            _SUBSCRIPTION_CACHE.pop(cache_key, None)
            return None
        return str(cached["content"])


def _set_cached_subscription(cache_key: tuple, content: str) -> None:
    user_key, config_format, as_base64, reverse, *_ = cache_key
    with _SUBSCRIPTION_CACHE_LOCK:
        keys_to_remove = [
            key for key in list(_SUBSCRIPTION_CACHE)
            if key[:4] == (user_key, config_format, as_base64, reverse)
        ]
        for key in keys_to_remove:
            _SUBSCRIPTION_CACHE.pop(key, None)
        _SUBSCRIPTION_CACHE[cache_key] = {
            "content": content,
            "expires_at": time() + _SUBSCRIPTION_CACHE_TTL_SECONDS,
        }


def _should_update_subscription_metadata(dbuser: User) -> bool:
    last_update = dbuser.sub_updated_at
    if not last_update:
        return True
    return datetime.utcnow() - last_update >= timedelta(seconds=_SUBSCRIPTION_METADATA_UPDATE_SECONDS)


def enforce_hwid_device_limit(
    db: Session,
    dbuser: User,
    request: Request,
    user_agent: str,
) -> tuple[bool, str | None]:
    mode = (
        "enabled"
        if dbuser.hwid_device_limit_enabled
        else "disabled"
        if dbuser.hwid_device_limit_enabled is not None
        else config_module.HWID_DEVICE_LIMIT_ENABLED
    )
    if mode == "disabled":
        return True, None

    hwid = request.headers.get("x-hwid")
    if not hwid:
        if mode == "logging":
            return True, None
        return False, "missing_hwid"

    if mode == "logging":
        try:
            crud.upsert_user_hwid_device(
                db=db,
                dbuser=dbuser,
                hwid=hwid,
                device_os=request.headers.get("x-device-os"),
                device_model=request.headers.get("x-device-model"),
                device_os_version=request.headers.get("x-ver-os"),
                user_agent=user_agent,
            )
        except OperationalError:
            logger.warning(
                "Failed to log HWID device for user %s due to database error; allowing subscription.",
                dbuser.id,
            )
        return True, None

    limit = (
        dbuser.hwid_device_limit
        if dbuser.hwid_device_limit is not None
        else config_module.HWID_FALLBACK_DEVICE_LIMIT
    )
    if limit <= 0:
        return True, None

    existing_device = crud.get_user_hwid_device(db, dbuser, hwid)
    if not existing_device:
        devices_count = crud.count_user_hwid_devices(db, dbuser)
        if devices_count >= limit:
            return False, "device_limit_exceeded"

    try:
        crud.upsert_user_hwid_device(
            db=db,
            dbuser=dbuser,
            hwid=hwid,
            device_os=request.headers.get("x-device-os"),
            device_model=request.headers.get("x-device-model"),
            device_os_version=request.headers.get("x-ver-os"),
            user_agent=user_agent,
        )
    except OperationalError:
        logger.warning(
            "Failed to store HWID device for user %s due to database error; allowing subscription.",
            dbuser.id,
        )
    return True, None


def _resolve_client_config(user_agent: str) -> dict:
    if re.match(r'^([Cc]lash-verge|[Cc]lash[-\.]?[Mm]eta|[Ff][Ll][Cc]lash|[Mm]ihomo)', user_agent):
        return client_config["clash-meta"]

    if re.match(r'^([Cc]lash|[Ss]tash)', user_agent):
        return client_config["clash"]

    if re.match(r'^(SFA|SFI|SFM|SFT|[Kk]aring|[Hh]iddify[Nn]ext)|.*sing[-b]?ox.*', user_agent, re.IGNORECASE):
        return client_config["sing-box"]

    if re.match(r'^(SS|SSR|SSD|SSS|Outline|Shadowsocks|SSconf)', user_agent):
        return client_config["outline"]

    if (config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_V2RAYN) and re.match(r'^v2rayN/(\d+\.\d+)', user_agent):
        version_str = re.match(r'^v2rayN/(\d+\.\d+)', user_agent).group(1)
        if LooseVersion(version_str) >= LooseVersion("6.40"):
            return client_config["v2ray-json"]
        return client_config["v2ray"]

    if (config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_V2RAYN) and re.match(r'^v2raytun/android', user_agent):
        return {
            **client_config["v2ray-json"],
            "as_base64": True,
        }

    if (config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_V2RAYN) and re.match(r'^v2raytun/ios', user_agent):
        return client_config["v2ray-json"]

    if (config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_V2RAYNG) and re.match(r'^v2rayNG/(\d+\.\d+\.\d+)', user_agent):
        version_str = re.match(r'^v2rayNG/(\d+\.\d+\.\d+)', user_agent).group(1)
        if LooseVersion(version_str) >= LooseVersion("1.8.29"):
            return client_config["v2ray-json"]
        if LooseVersion(version_str) >= LooseVersion("1.8.18"):
            return {
                **client_config["v2ray-json"],
                "reverse": True,
            }
        return client_config["v2ray"]

    if re.match(r'^[Ss]treisand', user_agent):
        if config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_STREISAND:
            return client_config["v2ray-json"]
        return client_config["v2ray"]

    if (config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_HAPP) and re.match(r'^Happ/(\d+\.\d+\.\d+)', user_agent):
        return client_config["v2ray-json"]

    if config_module.USE_CUSTOM_JSON_DEFAULT or config_module.USE_CUSTOM_JSON_FOR_NPVTUNNEL:
        if "ktor-client" in user_agent:
            return client_config["v2ray-json"]
        return client_config["v2ray"]

    return client_config["v2ray"]


def get_subscription_user_info(user: UserResponse) -> dict:
    """Retrieve user subscription information including upload, download, total data, and expiry."""
    return {
        "upload": 0,
        "download": user.used_traffic,
        "total": user.data_limit if user.data_limit is not None else 0,
        "expire": user.expire if user.expire is not None else 0,
    }


def _user_agent_matches(rule: str, user_agent: str) -> bool:
    if not rule:
        return False
    if rule == "*":
        return True
    if not user_agent:
        return False
    return rule.lower() in user_agent.lower()


def _apply_custom_subscription_headers(
    response_headers: dict[str, str], user_agent: str
) -> None:
    for entry in config_module.SUBSCRIPTION_CUSTOM_HEADERS:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", "")).strip()
        value = str(entry.get("value", "")).strip()
        rule = str(entry.get("user_agent", "")).strip()
        if not name or not value:
            continue
        if _user_agent_matches(rule, user_agent):
            response_headers[name] = value


@router.get("/{token}/")
@router.get("/{token}", include_in_schema=False)
def user_subscription(
    request: Request,
    db: Session = Depends(get_db),
    dbuser: UserResponse = Depends(get_validated_sub),
    user_agent: str = Header(default="")
):
    """Provides a subscription link based on the user agent (Clash, V2Ray, etc.)."""
    accept_header = request.headers.get("Accept", "")
    if "text/html" in accept_header:
        user: UserResponse = UserResponse.model_validate(dbuser)
        days_to_next_reset, next_reset_at = get_next_reset_info(dbuser)
        return HTMLResponse(
            render_template(
                config_module.SUBSCRIPTION_PAGE_TEMPLATE,
                {
                    "user": user,
                    "days_to_next_reset": days_to_next_reset,
                    "next_reset_at": next_reset_at,
                },
            )
        )

    user: UserResponse = UserResponse.model_validate(dbuser)
    response_headers = {
        "content-disposition": f'attachment; filename="{user.username}"',
        "profile-web-page-url": str(request.url),
        "support-url": config_module.SUB_SUPPORT_URL,
        "profile-title": encode_title(
            format_subscription_profile_title(user)
        ),
        "profile-update-interval": config_module.SUB_UPDATE_INTERVAL,
        "subscription-userinfo": "; ".join(
            f"{key}={val}"
            for key, val in get_subscription_user_info(user).items()
        )
    }
    _apply_custom_subscription_headers(response_headers, user_agent)

    allowed, _ = enforce_hwid_device_limit(db, dbuser, request, user_agent)
    if not allowed:
        notes = get_hwid_limit_notes()
        if not notes:
            return Response(status_code=200, content="", headers=response_headers)
        config = _resolve_client_config(user_agent)
        fake_conf = generate_fake_subscription(
            user=user,
            config_format=config["config_format"],
            as_base64=config["as_base64"],
            reverse=config["reverse"],
            notes=notes,
        )
        return Response(
            content=fake_conf,
            media_type=config["media_type"],
            headers=response_headers,
        )

    if _should_update_subscription_metadata(dbuser):
        crud.update_user_sub(db, dbuser, user_agent)
    config = _resolve_client_config(user_agent)
    cache_key = _build_subscription_cache_key(
        user=user,
        config_format=config["config_format"],
        as_base64=config["as_base64"],
        reverse=config["reverse"],
    )
    conf = _get_cached_subscription(cache_key)
    cache_status = "hit" if conf is not None else "miss"
    if conf is None:
        conf = generate_subscription(
            user=user,
            config_format=config["config_format"],
            as_base64=config["as_base64"],
            reverse=config["reverse"],
        )
        _set_cached_subscription(cache_key, conf)
    response_headers["x-subscription-cache"] = cache_status
    return Response(content=conf, media_type=config["media_type"], headers=response_headers)


@router.get("/{token}/info", response_model=SubscriptionUserResponse)
def user_subscription_info(
    request: Request,
    db: Session = Depends(get_db),
    dbuser: UserResponse = Depends(get_validated_sub),
    user_agent: str = Header(default=""),
):
    """Retrieves detailed information about the user's subscription."""
    allowed, _ = enforce_hwid_device_limit(db, dbuser, request, user_agent)
    if not allowed:
        return Response(status_code=200, content="")
    days_to_next_reset, next_reset_at = get_next_reset_info(dbuser)
    response = SubscriptionUserResponse.model_validate(dbuser)
    return response.model_copy(
        update={"days_to_next_reset": days_to_next_reset, "next_reset_at": next_reset_at}
    )


@router.get("/{token}/usage")
def user_get_usage(
    request: Request,
    dbuser: UserResponse = Depends(get_validated_sub),
    start: str = "",
    end: str = "",
    db: Session = Depends(get_db),
    user_agent: str = Header(default=""),
):
    """Fetches the usage statistics for the user within a specified date range."""
    allowed, _ = enforce_hwid_device_limit(db, dbuser, request, user_agent)
    if not allowed:
        return Response(status_code=200, content="")
    start, end = validate_dates(start, end)

    usages = crud.get_user_usages(db, dbuser, start, end)

    return {"usages": usages, "username": dbuser.username}


@router.get("/{token}/{client_type}")
def user_subscription_with_client_type(
    request: Request,
    dbuser: UserResponse = Depends(get_validated_sub),
    client_type: str = Path(..., regex="sing-box|clash-meta|clash|outline|v2ray|v2ray-json"),
    db: Session = Depends(get_db),
    user_agent: str = Header(default="")
):
    """Provides a subscription link based on the specified client type (e.g., Clash, V2Ray)."""
    user: UserResponse = UserResponse.model_validate(dbuser)
    response_headers = {
        "content-disposition": f'attachment; filename="{user.username}"',
        "profile-web-page-url": str(request.url),
        "support-url": config_module.SUB_SUPPORT_URL,
        "profile-title": encode_title(
            format_subscription_profile_title(user)
        ),
        "profile-update-interval": config_module.SUB_UPDATE_INTERVAL,
        "subscription-userinfo": "; ".join(
            f"{key}={val}"
            for key, val in get_subscription_user_info(user).items()
        )
    }
    _apply_custom_subscription_headers(response_headers, user_agent)

    allowed, _ = enforce_hwid_device_limit(db, dbuser, request, user_agent)
    if not allowed:
        notes = get_hwid_limit_notes()
        if not notes:
            return Response(status_code=200, content="", headers=response_headers)
        config = client_config.get(client_type)
        fake_conf = generate_fake_subscription(
            user=user,
            config_format=config["config_format"],
            as_base64=config["as_base64"],
            reverse=config["reverse"],
            notes=notes,
        )
        return Response(
            content=fake_conf,
            media_type=config["media_type"],
            headers=response_headers,
        )

    config = client_config.get(client_type)
    cache_key = _build_subscription_cache_key(
        user=user,
        config_format=config["config_format"],
        as_base64=config["as_base64"],
        reverse=config["reverse"],
    )
    conf = _get_cached_subscription(cache_key)
    cache_status = "hit" if conf is not None else "miss"
    if conf is None:
        conf = generate_subscription(
            user=user,
            config_format=config["config_format"],
            as_base64=config["as_base64"],
            reverse=config["reverse"],
        )
        _set_cached_subscription(cache_key, conf)
    response_headers["x-subscription-cache"] = cache_status

    return Response(content=conf, media_type=config["media_type"], headers=response_headers)
