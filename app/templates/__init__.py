from datetime import datetime
from typing import Union

import jinja2

import config as config_module

from .filters import CUSTOM_FILTERS

_env: jinja2.Environment | None = None
_custom_templates_directory: str | None = None


def _build_environment(custom_directory: str | None) -> jinja2.Environment:
    template_directories = ["app/templates"]
    if custom_directory:
        # User's templates have priority over default templates
        template_directories.insert(0, custom_directory)
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_directories)
    )
    environment.filters.update(CUSTOM_FILTERS)
    environment.globals["now"] = datetime.utcnow
    return environment


def _ensure_environment() -> jinja2.Environment:
    global _env, _custom_templates_directory
    custom_directory = config_module.CUSTOM_TEMPLATES_DIRECTORY
    if _env is None or custom_directory != _custom_templates_directory:
        _custom_templates_directory = custom_directory
        _env = _build_environment(custom_directory)
    return _env


def render_template(template: str, context: Union[dict, None] = None) -> str:
    env = _ensure_environment()
    return env.get_template(template).render(context or {})
