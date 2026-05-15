"""
Auto-generated shim for core/ package.
Adds this directory to sys.path so all old-style bare imports still work.
"""
import sys, os
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from . import multi_agent_livekit as multi_agent_livekit  # noqa: F401
from . import multi_agent as multi_agent  # noqa: F401
from . import background_worker as background_worker  # noqa: F401
from . import memory_store as memory_store  # noqa: F401
from . import goal_manager as goal_manager  # noqa: F401
from . import audit_log as audit_log  # noqa: F401
from . import screen_share as screen_share  # noqa: F401
from . import bridge as bridge  # noqa: F401
from . import tools_safety as tools_safety  # noqa: F401
