import base64
import random
import secrets
from collections import defaultdict
from datetime import datetime as dt
from datetime import timedelta
from typing import TYPE_CHECKING, List, Literal, Union
from uuid import uuid4

from jdatetime import date as jd

from app import xray
from app.utils.system import get_public_ip, get_public_ipv6, readable_size

from . import *

if TYPE_CHECKING:
    from app.models.user import UserResponse

import config as config_module

SERVER_IP = get_public_ip()
SERVER_IPV6 = get_public_ipv6()

STATUS_EMOJIS = {
    "active": "✅",
    "expired": "⌛️",
    "limited": "🪫",
    "disabled": "❌",
    "on_hold": "🔌",
}

def get_status_texts() -> dict[str, str]:
    return {
        "active": config_module.ACTIVE_STATUS_TEXT,
        "expired": config_module.EXPIRED_STATUS_TEXT,
        "limited": config_module.LIMITED_STATUS_TEXT,
        "disabled": config_module.DISABLED_STATUS_TEXT,
        "on_hold": config_module.ONHOLD_STATUS_TEXT,
    }

DEFAULT_HOST_REMARK = "🚀 Marz ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]"
DEFAULT_HOST_ADDRESS_TOKENS = {"{SERVER_IP}", "{SERVER_IPV6}"}


def is_default_host(host: dict) -> bool:
    address = host.get("address") or []
    return (
        host.get("remark") == DEFAULT_HOST_REMARK
        and len(address) == 1
        and address[0] in DEFAULT_HOST_ADDRESS_TOKENS
    )


def generate_v2ray_links(
        proxies: dict,
        inbounds: dict,
        extra_data: dict,
        reverse: bool,
        custom_remarks: list[str] | None = None,
) -> list:
    format_variables = setup_format_variables(extra_data)
    conf = V2rayShareLink()
    return process_inbounds_and_tags(
        inbounds,
        proxies,
        format_variables,
        conf=conf,
        reverse=reverse,
        custom_remarks=custom_remarks,
    )


def get_status_notes(status: str | object) -> list[str]:
    if hasattr(status, "value"):
        status = status.value
    return config_module.SUBSCRIPTION_CUSTOM_NOTES.get(status, [])


def get_hwid_limit_notes() -> list[str]:
    return config_module.SUBSCRIPTION_CUSTOM_NOTES.get("hwid_limit", [])


def _fake_protocol_for_format(config_format: str) -> str:
    if config_format == "outline":
        return "shadowsocks"
    return "vmess"


def _build_fake_inbound(protocol: str) -> dict:
    return {
        "protocol": protocol,
        "network": "tcp",
        "port": 443,
        "tls": "tls",
        "sni": "example.com",
        "host": "",
        "path": "",
        "header_type": "none",
        "ais": "",
        "fp": "",
        "pbk": "",
        "sid": "",
        "spx": "",
        "alpn": "",
        "mux_enable": False,
        "fragment_setting": "",
        "noise_setting": "",
        "random_user_agent": False,
        "allowinsecure": "",
        "multiMode": False,
        "downloadSettings": {},
    }


def _build_fake_settings(protocol: str) -> dict:
    if protocol == "shadowsocks":
        return {
            "password": secrets.token_urlsafe(16),
            "method": "aes-128-gcm",
        }
    return {
        "id": str(uuid4()),
        "flow": "",
    }


def _has_balancer_tags(balancer_tags: object) -> bool:
    if isinstance(balancer_tags, str):
        return bool(balancer_tags.strip())
    if isinstance(balancer_tags, list):
        return any(str(tag).strip() for tag in balancer_tags)
    return False


def _is_json_only_host(inbound: dict) -> bool:
    outbound_tag = inbound.get("outbound_tag")
    balancer_tags = inbound.get("balancer_tags")
    return bool(outbound_tag and _has_balancer_tags(balancer_tags))


def generate_fake_subscription(
    user: "UserResponse",
    config_format: Literal["v2ray", "clash-meta", "clash", "sing-box", "outline", "v2ray-json"],
    as_base64: bool,
    reverse: bool,
    notes: list[str],
) -> str:
    if not notes:
        return ""

    format_variables = setup_format_variables(user.model_dump())
    protocol = _fake_protocol_for_format(config_format)
    format_variables.update({"PROTOCOL": protocol, "TRANSPORT": "tcp"})
    formatted_notes = [
        note.format_map(format_variables)
        for note in notes
    ]

    if config_format == "v2ray":
        conf: Union[V2rayShareLink, V2rayJsonConfig, SingBoxConfiguration, ClashConfiguration, ClashMetaConfiguration, OutlineConfiguration] = V2rayShareLink()
    elif config_format == "clash-meta":
        conf = ClashMetaConfiguration()
    elif config_format == "clash":
        conf = ClashConfiguration()
    elif config_format == "sing-box":
        conf = SingBoxConfiguration()
    elif config_format == "outline":
        conf = OutlineConfiguration()
    elif config_format == "v2ray-json":
        conf = V2rayJsonConfig()
    else:
        raise ValueError(f'Unsupported format "{config_format}"')

    notes_to_use = formatted_notes[:1] if config_format == "outline" else formatted_notes
    for idx, note in enumerate(notes_to_use, start=1):
        inbound = _build_fake_inbound(protocol)
        settings = _build_fake_settings(protocol)
        address = "127.0.0.1"
        conf.add(
            remark=note,
            address=address,
            inbound=inbound,
            settings=settings,
        )

    if config_format == "v2ray":
        links = list(reversed(conf.links)) if reverse else conf.links
        config = "\n".join(links)
    else:
        config = conf.render(reverse=reverse)
        if isinstance(config, list):
            config = "\n".join(config)
    if as_base64:
        config = base64.b64encode(config.encode()).decode()
    return config


def generate_clash_subscription(
        proxies: dict,
        inbounds: dict,
        extra_data: dict,
        reverse: bool,
        is_meta: bool = False,
        custom_remarks: list[str] | None = None,
) -> str:
    if is_meta is True:
        conf = ClashMetaConfiguration()
    else:
        conf = ClashConfiguration()

    format_variables = setup_format_variables(extra_data)
    return process_inbounds_and_tags(
        inbounds,
        proxies,
        format_variables,
        conf=conf,
        reverse=reverse,
        custom_remarks=custom_remarks,
    )


def generate_singbox_subscription(
        proxies: dict,
        inbounds: dict,
        extra_data: dict,
        reverse: bool,
        custom_remarks: list[str] | None = None,
) -> str:
    conf = SingBoxConfiguration()

    format_variables = setup_format_variables(extra_data)
    return process_inbounds_and_tags(
        inbounds,
        proxies,
        format_variables,
        conf=conf,
        reverse=reverse,
        custom_remarks=custom_remarks,
    )


def generate_outline_subscription(
        proxies: dict,
        inbounds: dict,
        extra_data: dict,
        reverse: bool,
        custom_remarks: list[str] | None = None,
) -> str:
    conf = OutlineConfiguration()

    format_variables = setup_format_variables(extra_data)
    return process_inbounds_and_tags(
        inbounds,
        proxies,
        format_variables,
        conf=conf,
        reverse=reverse,
        custom_remarks=custom_remarks,
    )


def generate_v2ray_json_subscription(
        proxies: dict,
        inbounds: dict,
        extra_data: dict,
        reverse: bool,
        custom_remarks: list[str] | None = None,
) -> str:
    conf = V2rayJsonConfig()

    format_variables = setup_format_variables(extra_data)
    return process_inbounds_and_tags(
        inbounds,
        proxies,
        format_variables,
        conf=conf,
        reverse=reverse,
        custom_remarks=custom_remarks,
    )


def generate_subscription(
        user: "UserResponse",
        config_format: Literal["v2ray", "clash-meta", "clash", "sing-box", "outline", "v2ray-json"],
        as_base64: bool,
        reverse: bool,
) -> str:
    kwargs = {
        "proxies": user.proxies,
        "inbounds": user.inbounds,
        "extra_data": user.model_dump(),
        "reverse": reverse,
    }
    status = user.status
    if hasattr(status, "value"):
        status = status.value
    status_notes = get_status_notes(status)
    custom_remarks = status_notes if status_notes and status in {"expired", "limited", "disabled"} else None

    if config_format == "v2ray":
        config = "\n".join(generate_v2ray_links(**kwargs, custom_remarks=custom_remarks))
    elif config_format == "clash-meta":
        config = generate_clash_subscription(**kwargs, is_meta=True, custom_remarks=custom_remarks)
    elif config_format == "clash":
        config = generate_clash_subscription(**kwargs, custom_remarks=custom_remarks)
    elif config_format == "sing-box":
        config = generate_singbox_subscription(**kwargs, custom_remarks=custom_remarks)
    elif config_format == "outline":
        config = generate_outline_subscription(**kwargs, custom_remarks=custom_remarks)
    elif config_format == "v2ray-json":
        config = generate_v2ray_json_subscription(**kwargs, custom_remarks=custom_remarks)
    else:
        raise ValueError(f'Unsupported format "{config_format}"')

    if as_base64:
        if isinstance(config, list):
            config = "\n".join(config)
        config = base64.b64encode(config.encode()).decode()

    return config


def format_time_left(seconds_left: int) -> str:
    if not seconds_left or seconds_left <= 0:
        return "∞"

    minutes, seconds = divmod(seconds_left, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    months, days = divmod(days, 30)

    result = []
    if months:
        result.append(f"{months}m")
    if days:
        result.append(f"{days}d")
    if hours and (days < 7):
        result.append(f"{hours}h")
    if minutes and not (months or days):
        result.append(f"{minutes}m")
    if seconds and not (months or days):
        result.append(f"{seconds}s")
    return " ".join(result)


def setup_format_variables(extra_data: dict) -> dict:
    from app.models.user import UserStatus

    user_status = extra_data.get("status")
    expire_timestamp = extra_data.get("expire")
    on_hold_expire_duration = extra_data.get("on_hold_expire_duration")
    now = dt.utcnow()
    now_ts = now.timestamp()

    if user_status != UserStatus.on_hold:
        if expire_timestamp is not None and expire_timestamp >= 0:
            seconds_left = expire_timestamp - int(dt.utcnow().timestamp())
            expire_datetime = dt.fromtimestamp(expire_timestamp)
            expire_date = expire_datetime.date()
            jalali_expire_date = jd.fromgregorian(
                year=expire_date.year, month=expire_date.month, day=expire_date.day
            ).strftime("%Y-%m-%d")
            if now_ts < expire_timestamp:
                days_left = (expire_datetime - dt.utcnow()).days + 1
                time_left = format_time_left(seconds_left)
            else:
                days_left = "0"
                time_left = "0"

        else:
            days_left = "∞"
            time_left = "∞"
            expire_date = "∞"
            jalali_expire_date = "∞"
    else:
        if on_hold_expire_duration is not None and on_hold_expire_duration >= 0:
            days_left = timedelta(seconds=on_hold_expire_duration).days
            time_left = format_time_left(on_hold_expire_duration)
            expire_date = "-"
            jalali_expire_date = "-"
        else:
            days_left = "∞"
            time_left = "∞"
            expire_date = "∞"
            jalali_expire_date = "∞"

    if extra_data.get("data_limit"):
        data_limit = readable_size(extra_data["data_limit"])
        data_left = extra_data["data_limit"] - extra_data["used_traffic"]
        usage_Percentage = round((extra_data["used_traffic"] / extra_data["data_limit"]) * 100.0, 2)

        if data_left < 0:
            data_left = 0
        data_left = readable_size(data_left)
    else:
        data_limit = "∞"
        data_left = "∞"
        usage_Percentage = "∞"

    status_emoji = STATUS_EMOJIS.get(extra_data.get("status")) or ""
    status_template = get_status_texts().get(extra_data.get("status")) or ""

    # Create a temporary dictionary with variables excluding STATUS_TEXT
    temp_vars = {
        "SERVER_IP": SERVER_IP,
        "SERVER_IPV6": SERVER_IPV6,
        "USERNAME": extra_data.get("username", "{USERNAME}"),
        "DATA_USAGE": readable_size(extra_data.get("used_traffic")),
        "DATA_LIMIT": data_limit,
        "DATA_LEFT": data_left,
        "DAYS_LEFT": days_left,
        "EXPIRE_DATE": expire_date,
        "JALALI_EXPIRE_DATE": jalali_expire_date,
        "TIME_LEFT": time_left,
        "STATUS_EMOJI": status_emoji,
        "USAGE_PERCENTAGE": usage_Percentage,
    }

    # Format the status text using the temporary variables
    status_text = status_template.format_map(defaultdict(lambda: "<missing>", temp_vars))

    # Create the final format_variables including the formatted STATUS_TEXT
    format_variables = defaultdict(
        lambda: "<missing>",
        {
            **temp_vars,
            "STATUS_TEXT": status_text,
        },
    )

    return format_variables


def format_subscription_profile_title(
    user: "UserResponse",
    template: str | None = None,
) -> str:
    raw_template = template or config_module.SUB_PROFILE_TITLE
    format_variables = setup_format_variables(user.model_dump())
    return raw_template.format_map(format_variables)


def process_inbounds_and_tags(
        inbounds: dict,
        proxies: dict,
        format_variables: dict,
        conf: Union[
            V2rayShareLink,
            V2rayJsonConfig,
            SingBoxConfiguration,
            ClashConfiguration,
            ClashMetaConfiguration,
            OutlineConfiguration
        ],
        reverse=False,
        custom_remarks: list[str] | None = None,
) -> Union[List, str]:
    _inbounds = []
    for protocol, tags in inbounds.items():
        for tag in tags:
            _inbounds.append((protocol, [tag]))
    index_dict = {proxy: index for index, proxy in enumerate(
        xray.config.inbounds_by_tag.keys())}
    inbounds = sorted(
        _inbounds, key=lambda x: index_dict.get(x[1][0], float('inf')))

    entries = []
    for protocol, tags in inbounds:
        settings = proxies.get(protocol)
        if not settings:
            continue

        format_variables.update({"PROTOCOL": protocol.name})
        for tag in tags:
            inbound = xray.config.inbounds_by_tag.get(tag)
            if not inbound:
                continue

            format_variables.update({"TRANSPORT": inbound["network"]})
            hosts = xray.hosts.get(tag, [])
            if hosts:
                default_hosts = [host for host in hosts if is_default_host(host)]
                custom_hosts = [host for host in hosts if not is_default_host(host)]
                if custom_hosts:
                    hosts = (
                        custom_hosts
                        if config_module.SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS
                        else custom_hosts + default_hosts
                    )
                if isinstance(conf, V2rayJsonConfig):
                    def merge_priority(host: dict) -> bool:
                        return bool(
                            host.get("merge_primary")
                            and host.get("outbound_tag")
                            and host.get("balancer_tags")
                        )

                    hosts = sorted(hosts, key=merge_priority)

            for host in hosts:
                if not isinstance(conf, V2rayJsonConfig) and _is_json_only_host(host):
                    continue
                host_inbound = inbound.copy()
                sni = ""
                sni_list = host["sni"] or inbound["sni"]
                if sni_list:
                    salt = secrets.token_hex(8)
                    sni = random.choice(sni_list).replace("*", salt)

                sid_value = inbound.get("sid")
                if sids := inbound.get("sids"):
                    sid_value = random.choice(sids)

                req_host = ""
                req_host_list = host["host"] or inbound["host"]
                if req_host_list:
                    salt = secrets.token_hex(8)
                    req_host = random.choice(req_host_list).replace("*", salt)

                address = ""
                address_list = host['address']
                if host['address']:
                    salt = secrets.token_hex(8)
                    address = random.choice(address_list).replace('*', salt)

                if host["path"] is not None:
                    path = host["path"].format_map(format_variables)
                else:
                    path = inbound.get("path", "").format_map(format_variables)

                if host.get("use_sni_as_host", False) and sni:
                    req_host = sni

                host_update = {
                    "port": host["port"] or inbound["port"],
                    "sni": sni,
                    "host": req_host,
                    "tls": inbound["tls"] if host["tls"] is None else host["tls"],
                    "alpn": host["alpn"] if host["alpn"] else None,
                    "path": path,
                    "fp": host["fingerprint"] or inbound.get("fp", ""),
                    "ais": host["allowinsecure"] or inbound.get("allowinsecure", ""),
                    "mux_enable": host["mux_enable"],
                    "fragment_setting": host["fragment_setting"],
                    "noise_setting": host["noise_setting"],
                    "random_user_agent": host["random_user_agent"],
                    "sid": sid_value or "",
                    "outbound_tag": host.get("outbound_tag"),
                    "balancer_tags": host.get("balancer_tags"),
                }
                host_inbound.update(host_update)

                entries.append(
                    {
                        "remark": host["remark"].format_map(format_variables),
                        "address": address.format_map(format_variables),
                        "inbound": host_inbound,
                        "settings": settings.model_dump(),
                        "format_variables": format_variables.copy(),
                    }
                )

    if custom_remarks:
        total_entries = len(entries)
        if reverse:
            target_indices = list(
                range(total_entries - 1, max(total_entries - len(custom_remarks), 0) - 1, -1)
            )
        else:
            target_indices = list(range(0, min(total_entries, len(custom_remarks))))

        for note, idx in zip(custom_remarks, target_indices):
            entry = entries[idx]
            entry["remark"] = note.format_map(entry["format_variables"])

        if config_module.SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS:
            target_index_set = set(target_indices)
            entries = [entry for idx, entry in enumerate(entries) if idx in target_index_set]

    for entry in entries:
        if not isinstance(conf, V2rayJsonConfig) and _is_json_only_host(entry["inbound"]):
            continue
        conf.add(
            remark=entry["remark"],
            address=entry["address"],
            inbound=entry["inbound"],
            settings=entry["settings"],
        )

    return conf.render(reverse=reverse)


def encode_title(text: str) -> str:
    return f"base64:{base64.b64encode(text.encode()).decode()}"
