"""
Auto-generated shim for llm/ package.
Adds this directory to sys.path so all old-style bare imports still work.
"""
import sys, os
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from . import aws_nova_llm as aws_nova_llm  # noqa: F401
from . import aws_config as aws_config  # noqa: F401
from . import enhanced_llm as enhanced_llm  # noqa: F401
from . import azure_openai_llm as azure_openai_llm  # noqa: F401
from . import edge_tts_plugin as edge_tts_plugin  # noqa: F401
from . import prompts as prompts  # noqa: F401
from . import infin_prompts as infin_prompts  # noqa: F401
from . import browser_agent_prompts as browser_agent_prompts  # noqa: F401
