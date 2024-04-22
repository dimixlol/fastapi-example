from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .config import get_settings

settings = get_settings()

templates = Jinja2Templates(directory=settings.base_dir / "templates")
static = StaticFiles(directory=settings.base_dir / "static")
