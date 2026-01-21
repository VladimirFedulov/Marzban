import time
import traceback

from app import app, logger, scheduler, xray
from app.db import GetDB, crud
from app.models.node import NodeStatus
import config as config_module
from xray_api import exc as xray_exc


def core_health_check():
    config = None

    # main core
    if not xray.core.started:
        if not config:
            config = xray.config.include_db_users()
        xray.core.restart(config)

    # nodes' core
    for node_id, node in list(xray.nodes.items()):
        error_message = None
        try:
            node_connected = node.connected
        except Exception as exc:
            node_connected = False
            error_message = str(exc)

        if node_connected:
            try:
                assert node.started
                node.api.get_sys_stats(timeout=2)
                xray.operations.mark_node_connected(node_id)
            except (ConnectionError, xray_exc.XrayError, AssertionError) as exc:
                xray.operations.mark_node_error(node_id, str(exc))
                if not config:
                    config = xray.config.include_db_users()
                xray.operations.restart_node(
                    node_id,
                    config,
                    reason=f"Health check failed: {exc}",
                )
        else:
            xray.operations.mark_node_error(node_id, error_message or "Node ping failed")
            if not config:
                config = xray.config.include_db_users()
            if xray.operations.should_force_reconnect(node_id):
                xray.operations.force_reconnect_node(node_id, config)
            else:
                xray.operations.connect_node(node_id, config)


@app.on_event("startup")
def start_core():
    logger.info("Generating Xray core config")

    start_time = time.time()
    config = xray.config.include_db_users()
    logger.info(f"Xray core config generated in {(time.time() - start_time):.2f} seconds")

    # main core
    logger.info("Starting main Xray core")
    try:
        xray.core.start(config)
    except Exception:
        traceback.print_exc()

    # nodes' core
    logger.info("Starting nodes Xray core")
    with GetDB() as db:
        dbnodes = crud.get_nodes(db=db, enabled=True)
        node_ids = [dbnode.id for dbnode in dbnodes]
        for dbnode in dbnodes:
            crud.update_node_status(db, dbnode, NodeStatus.connecting)

    for node_id in node_ids:
        xray.operations.connect_node(node_id, config)

    scheduler.add_job(core_health_check, 'interval',
                      seconds=config_module.JOB_CORE_HEALTH_CHECK_INTERVAL,
                      coalesce=True,
                      max_instances=config_module.JOB_CORE_HEALTH_CHECK_MAX_INSTANCES)


@app.on_event("shutdown")
def app_shutdown():
    logger.info("Stopping main Xray core")
    xray.core.stop()

    logger.info("Stopping nodes Xray core")
    for node in list(xray.nodes.values()):
        try:
            node.disconnect()
        except Exception:
            pass
