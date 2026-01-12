from app import logger, scheduler
from app.db import GetDB, crud
from config import HWID_DEVICE_RETENTION_DAYS, JOB_HWID_DEVICE_CLEANUP_INTERVAL


def cleanup_hwid_devices():
    if HWID_DEVICE_RETENTION_DAYS < 0:
        return
    with GetDB() as db:
        crud.delete_expired_hwid_devices(db, HWID_DEVICE_RETENTION_DAYS)


scheduler.add_job(
    cleanup_hwid_devices,
    "interval",
    seconds=JOB_HWID_DEVICE_CLEANUP_INTERVAL,
    coalesce=True,
    max_instances=1,
)
