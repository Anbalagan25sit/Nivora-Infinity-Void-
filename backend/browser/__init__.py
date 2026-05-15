"""
Auto-generated shim for browser/ package.
Adds this directory to sys.path so all old-style bare imports still work.
"""
import sys, os
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from . import browser_agent as browser_agent  # noqa: F401
from . import browser_automation as browser_automation  # noqa: F401
from . import browser_use_adapter as browser_use_adapter  # noqa: F401
from . import browser_use_agent as browser_use_agent  # noqa: F401
from . import browser_use_tools as browser_use_tools  # noqa: F401
from . import browser_use_langgraph as browser_use_langgraph  # noqa: F401
from . import browser_use_langgraph_tools as browser_use_langgraph_tools  # noqa: F401
from . import universal_web_agent as universal_web_agent  # noqa: F401
from . import universal_web_tools as universal_web_tools  # noqa: F401
from . import computer_use as computer_use  # noqa: F401
from . import cookie_manager as cookie_manager  # noqa: F401
from . import global_browser as global_browser  # noqa: F401
from . import web_scraper as web_scraper  # noqa: F401
from . import anime_browser as anime_browser  # noqa: F401
from . import anime_browser_advanced as anime_browser_advanced  # noqa: F401
from . import ebox_automation as ebox_automation  # noqa: F401
