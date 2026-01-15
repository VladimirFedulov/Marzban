from fastapi import APIRouter
from . import (
    admin, 
    core, 
    node, 
    settings,
    subscription, 
    system, 
    user_template, 
    user,
    home,
)

api_router = APIRouter()

routers = [
    admin.router,
    core.router,
    node.router,
    settings.router,
    subscription.router,
    system.router,
    user_template.router,
    user.router,
    home.router,
]

for router in routers:
    api_router.include_router(router)

__all__ = ["api_router"]
