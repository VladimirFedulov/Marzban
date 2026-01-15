from app import logger, scheduler
from app.db import GetDB, crud
import config as config_module


def cleanup_hwid_devices():
    if config_module.HWID_DEVICE_RETENTION_DAYS < 0:
        return
    with GetDB() as db:
        crud.delete_expired_hwid_devices(
            db, config_module.HWID_DEVICE_RETENTION_DAYS
        )


scheduler.add_job(
    cleanup_hwid_devices,
    "interval",
    seconds=config_module.JOB_HWID_DEVICE_CLEANUP_INTERVAL,
    coalesce=True,
    max_instances=1,
)
