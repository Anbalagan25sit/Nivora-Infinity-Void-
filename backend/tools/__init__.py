"""
Shim for tools/ package.
Re-exports everything from tools.py (ALL_TOOLS + every function tool)
so that `from tools import ALL_TOOLS` and `from tools import open_website`
continue to work unchanged from agent.py and multi_agent_livekit.py.
"""
import sys, os

_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

# Wildcard re-export — makes ALL_TOOLS, open_website, web_search etc.
# importable directly from the 'tools' package
from .tools import *              # noqa: F401, F403
from .tools import ALL_TOOLS      # noqa: F401  (explicit so static analysers see it)
from . import deep_research_tools # noqa: F401
from . import github_tool         # noqa: F401
from . import desktop_control     # noqa: F401
