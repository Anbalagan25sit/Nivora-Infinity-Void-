"""
Auto-generated shim for media/ package.
Adds this directory to sys.path so all old-style bare imports still work.
"""
import sys, os
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from . import spotify_api as spotify_api  # noqa: F401
from . import spotify_control as spotify_control  # noqa: F401
from . import spotify_tool as spotify_tool  # noqa: F401
from . import spotify_tools_advanced as spotify_tools_advanced  # noqa: F401
from . import youtube_automation as youtube_automation  # noqa: F401
from . import social_automation as social_automation  # noqa: F401
