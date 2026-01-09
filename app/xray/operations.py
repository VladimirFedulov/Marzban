from functools import lru_cache
import threading
import time
from typing import TYPE_CHECKING, Dict, List, Tuple

from sqlalchemy.exc import SQLAlchemyError

from app import logger, xray
from app.db import GetDB, crud
from app.models.node import NodeStatus
from app.models.user import UserResponse
from app.utils.concurrency import threaded_function
from app.xray.node import XRayNode
from xray_api import XRay as XRayAPI
from xray_api.types.account import Account, XTLSFlows

if TYPE_CHECKING:
    from app.db import User as DBUser
    from app.db.models import Node as DBNode


@lru_cache(maxsize=None)
def get_tls():
    from app.db import GetDB, get_tls_certificate
    with GetDB() as db:
        tls = get_tls_certificate(db)
        return {
            "key": tls.key,
            "certificate": tls.certificate
        }


@threaded_function
def _add_user_to_inbound(api: XRayAPI, inbound_tag: str, account: Account):
    try:
        api.add_inbound_user(tag=inbound_tag, user=account, timeout=30)
    except (
        xray.exc.EmailExistsError,
        xray.exc.ConnectionError,
        xray.exc.TagNotFoundError,
        xray.exc.TimeoutError,
    ):
        pass


@threaded_function
def _remove_user_from_inbound(api: XRayAPI, inbound_tag: str, email: str):
    try:
        api.remove_inbound_user(tag=inbound_tag, email=email, timeout=30)
    except (
        xray.exc.EmailNotFoundError,
        xray.exc.ConnectionError,
        xray.exc.TagNotFoundError,
        xray.exc.TimeoutError,
    ):
        pass


@threaded_function
def _alter_inbound_user(api: XRayAPI, inbound_tag: str, account: Account):
    try:
        api.remove_inbound_user(tag=inbound_tag, email=account.email, timeout=30)
    except (
        xray.exc.EmailNotFoundError,
        xray.exc.ConnectionError,
        xray.exc.TagNotFoundError,
        xray.exc.TimeoutError,
    ):
        pass
    try:
        api.add_inbound_user(tag=inbound_tag, user=account, timeout=30)
    except (
        xray.exc.EmailExistsError,
        xray.exc.ConnectionError,
        xray.exc.TagNotFoundError,
        xray.exc.TimeoutError,
    ):
        pass


def add_user(dbuser: "DBUser"):
    user = UserResponse.model_validate(dbuser)
    email = f"{dbuser.id}.{dbuser.username}"
    healthy_nodes = get_healthy_nodes()

    for proxy_type, inbound_tags in user.inbounds.items():
        for inbound_tag in inbound_tags:
            inbound = xray.config.inbounds_by_tag.get(inbound_tag, {})

            try:
                proxy_settings = user.proxies[proxy_type].dict(no_obj=True)
            except KeyError:
                pass
            account = proxy_type.account_model(email=email, **proxy_settings)

            # XTLS currently only supports transmission methods of TCP and mKCP
            if getattr(account, 'flow', None) and (
                inbound.get('network', 'tcp') not in ('tcp', 'raw', 'kcp')
                or
                (
                    inbound.get('network', 'tcp') in ('tcp', 'raw', 'kcp')
                    and
                    inbound.get('tls') not in ('tls', 'reality')
                )
                or
                inbound.get('header_type') == 'http'
            ):
                account.flow = XTLSFlows.NONE

            _add_user_to_inbound(xray.api, inbound_tag, account)  # main core
            for node_id, node in healthy_nodes:
                try:
                    _add_user_to_inbound(node.api, inbound_tag, account)
                except Exception as e:
                    logger.warning(
                        f"XRAY node add failed for user \"{dbuser.username}\" on inbound \"{inbound_tag}\""
                        f" (node {node_id}): {e}"
                    )


def remove_user(dbuser: "DBUser"):
    email = f"{dbuser.id}.{dbuser.username}"
    healthy_nodes = get_healthy_nodes()

    for inbound_tag in xray.config.inbounds_by_tag:
        _remove_user_from_inbound(xray.api, inbound_tag, email)
        for node_id, node in healthy_nodes:
            try:
                _remove_user_from_inbound(node.api, inbound_tag, email)
            except Exception as e:
                logger.warning(
                    f"XRAY node remove failed for user \"{dbuser.username}\" on inbound \"{inbound_tag}\""
                    f" (node {node_id}): {e}"
                )


def update_user(dbuser: "DBUser"):
    user = UserResponse.model_validate(dbuser)
    email = f"{dbuser.id}.{dbuser.username}"
    healthy_nodes = get_healthy_nodes()

    active_inbounds = []
    for proxy_type, inbound_tags in user.inbounds.items():
        for inbound_tag in inbound_tags:
            active_inbounds.append(inbound_tag)
            inbound = xray.config.inbounds_by_tag.get(inbound_tag, {})

            try:
                proxy_settings = user.proxies[proxy_type].dict(no_obj=True)
            except KeyError:
                pass
            account = proxy_type.account_model(email=email, **proxy_settings)

            # XTLS currently only supports transmission methods of TCP and mKCP
            if getattr(account, 'flow', None) and (
                inbound.get('network', 'tcp') not in ('tcp', 'kcp')
                or
                (
                    inbound.get('network', 'tcp') in ('tcp', 'kcp')
                    and
                    inbound.get('tls') not in ('tls', 'reality')
                )
                or
                inbound.get('header_type') == 'http'
            ):
                account.flow = XTLSFlows.NONE

            _alter_inbound_user(xray.api, inbound_tag, account)  # main core
            for node_id, node in healthy_nodes:
                try:
                    _alter_inbound_user(node.api, inbound_tag, account)
                except Exception as e:
                    logger.warning(
                        f"XRAY node alter failed for user \"{dbuser.username}\" on inbound \"{inbound_tag}\""
                        f" (node {node_id}): {e}"
                    )

    for inbound_tag in xray.config.inbounds_by_tag:
        if inbound_tag in active_inbounds:
            continue
        # remove disabled inbounds
        _remove_user_from_inbound(xray.api, inbound_tag, email)
        for node_id, node in healthy_nodes:
            try:
                _remove_user_from_inbound(node.api, inbound_tag, email)
            except Exception as e:
                logger.warning(
                    f"XRAY node remove (disabled inbound) failed for user \"{dbuser.username}\" on inbound \"{inbound_tag}\""
                    f" (node {node_id}): {e}"
                )


def remove_node(node_id: int):
    if node_id in xray.nodes:
        try:
            xray.nodes[node_id].disconnect()
        except Exception:
            pass
        finally:
            try:
                del xray.nodes[node_id]
            except KeyError:
                pass


def add_node(dbnode: "DBNode"):
    remove_node(dbnode.id)

    tls = get_tls()
    xray.nodes[dbnode.id] = XRayNode(address=dbnode.address,
                                     port=dbnode.port,
                                     api_port=dbnode.api_port,
                                     ssl_key=tls['key'],
                                     ssl_cert=tls['certificate'],
                                     usage_coefficient=dbnode.usage_coefficient)

    return xray.nodes[dbnode.id]


def _change_node_status(node_id: int, status: NodeStatus, message: str = None, version: str = None):
    with GetDB() as db:
        try:
            dbnode = crud.get_node_by_id(db, node_id)
            if not dbnode:
                return

            if dbnode.status == NodeStatus.disabled:
                remove_node(dbnode.id)
                return

            if status == NodeStatus.disabled:
                version = None
            elif version is None:
                version = dbnode.xray_version

            if (
                dbnode.status == status
                and dbnode.message == message
                and dbnode.xray_version == version
            ):
                return

            crud.update_node_status(db, dbnode, status, message, version)
        except SQLAlchemyError:
            db.rollback()


def mark_node_error(node_id: int, message: str):
    _set_node_health(node_id, False)
    _change_node_status(node_id, NodeStatus.error, message=message)


global _connecting_nodes
_connecting_nodes = {}
_connection_lock = threading.Lock()
_connection_backoff = {}
_node_health: Dict[int, Dict[str, float]] = {}
_node_health_lock = threading.Lock()
_node_health_ttl = 30.0


def _set_node_health(node_id: int, ok: bool):
    with _node_health_lock:
        _node_health[node_id] = {"ok": ok, "checked_at": time.monotonic()}


def get_healthy_nodes() -> List[Tuple[int, XRayNode]]:
    now = time.monotonic()
    healthy_nodes: List[Tuple[int, XRayNode]] = []
    with _node_health_lock:
        for node_id, node in list(xray.nodes.items()):
            entry = _node_health.get(node_id)
            if not entry:
                continue
            if not entry.get("ok"):
                continue
            if now - entry.get("checked_at", 0) > _node_health_ttl:
                continue
            healthy_nodes.append((node_id, node))
    return healthy_nodes


def _connection_allowed(node_id: int) -> bool:
    now = time.monotonic()
    with _connection_lock:
        entry = _connection_backoff.get(node_id)
        if not entry:
            return True
        return now >= entry["next_attempt"]


def _record_connection_failure(node_id: int):
    now = time.monotonic()
    with _connection_lock:
        entry = _connection_backoff.get(node_id, {"fails": 0, "next_attempt": now})
        entry["fails"] += 1
        backoff = min(60, 2 ** entry["fails"])
        entry["next_attempt"] = now + backoff
        _connection_backoff[node_id] = entry


def _clear_connection_backoff(node_id: int):
    with _connection_lock:
        _connection_backoff.pop(node_id, None)


@threaded_function
def connect_node(node_id, config=None):
    global _connecting_nodes

    if not _connection_allowed(node_id):
        return
    with _connection_lock:
        if _connecting_nodes.get(node_id):
            return

    with GetDB() as db:
        dbnode = crud.get_node_by_id(db, node_id)

    if not dbnode:
        return

    try:
        node = xray.nodes[dbnode.id]
        assert node.connected
    except (KeyError, AssertionError):
        node = xray.operations.add_node(dbnode)

    try:
        with _connection_lock:
            _connecting_nodes[node_id] = True

        _change_node_status(node_id, NodeStatus.connecting)
        logger.info(f"Connecting to \"{dbnode.name}\" node")

        if config is None:
            config = xray.config.include_db_users()

        node.start(config)
        version = node.get_version()
        _change_node_status(node_id, NodeStatus.connected, version=version)
        _set_node_health(node_id, True)
        logger.info(f"Connected to \"{dbnode.name}\" node, xray run on v{version}")
        _clear_connection_backoff(node_id)

    except Exception as e:
        _change_node_status(node_id, NodeStatus.error, message=str(e))
        _set_node_health(node_id, False)
        logger.info(f"Unable to connect to \"{dbnode.name}\" node: {e}")
        _record_connection_failure(node_id)

    finally:
        with _connection_lock:
            _connecting_nodes.pop(node_id, None)


@threaded_function
def restart_node(node_id, config=None):
    with GetDB() as db:
        dbnode = crud.get_node_by_id(db, node_id)

    if not dbnode:
        return

    try:
        node = xray.nodes[dbnode.id]
    except KeyError:
        node = xray.operations.add_node(dbnode)

    if not node.connected:
        return connect_node(node_id, config)

    try:
        logger.info(f"Restarting Xray core of \"{dbnode.name}\" node")

        if config is None:
            config = xray.config.include_db_users()

        node.restart(config)
        version = node.get_version()
        _change_node_status(node_id, NodeStatus.connected, version=version)
        _set_node_health(node_id, True)
        _clear_connection_backoff(node_id)
        logger.info(f"Xray core of \"{dbnode.name}\" node restarted")
    except Exception as e:
        _change_node_status(node_id, NodeStatus.error, message=str(e))
        _set_node_health(node_id, False)
        logger.info(f"Unable to restart node {node_id}: {e}")
        _record_connection_failure(node_id)
        try:
            node.disconnect()
        except Exception:
            pass


def mark_node_connected(node_id: int, version: str = None):
    _set_node_health(node_id, True)
    _change_node_status(node_id, NodeStatus.connected, version=version)


__all__ = [
    "add_user",
    "remove_user",
    "add_node",
    "remove_node",
    "connect_node",
    "mark_node_error",
    "mark_node_connected",
    "get_healthy_nodes",
    "restart_node",
]
