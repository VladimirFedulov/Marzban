from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.templates import render_template
import config as config_module

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def base():
    return render_template(config_module.HOME_PAGE_TEMPLATE)
