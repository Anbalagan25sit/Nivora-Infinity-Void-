"""
Safety Confirmation System for Nivora Desktop Automation

This module provides voice-based confirmation for destructive operations
and maintains a registry of tool safety levels.

Usage:
    from tools_safety import require_voice_confirmation, SafetyLevel

    confirmed = await require_voice_confirmation(
        context,
        "Delete file test.txt",
        "file_delete"
    )
"""

import logging
import asyncio
from enum import Enum
from typing import Optional, Dict
from dataclasses import dataclass
from livekit.agents import RunContext

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels for tool operations."""
    SAFE = "safe"  # No confirmation needed
    MEDIUM = "medium"  # Confirmation recommended
    DESTRUCTIVE = "destructive"  # Always requires confirmation


@dataclass
class ToolSafetyMeta:
    """Metadata for tool safety requirements."""
    level: SafetyLevel
    confirmation_prompt: str
    audit_tag: str
    requires_explicit_consent: bool = True


# Registry of tool safety metadata
TOOL_SAFETY_REGISTRY: Dict[str, ToolSafetyMeta] = {
    # File operations
    "file_delete": ToolSafetyMeta(
        level=SafetyLevel.DESTRUCTIVE,
        confirmation_prompt="permanently delete this file",
        audit_tag="file_deletion",
        requires_explicit_consent=True
    ),
    "file_write": ToolSafetyMeta(
        level=SafetyLevel.MEDIUM,
        confirmation_prompt="write to this file (may overwrite existing content)",
        audit_tag="file_write",
        requires_explicit_consent=True
    ),
    "file_move": ToolSafetyMeta(
        level=SafetyLevel.MEDIUM,
        confirmation_prompt="move this file",
        audit_tag="file_move",
        requires_explicit_consent=True
    ),
    "dir_delete": ToolSafetyMeta(
        level=SafetyLevel.DESTRUCTIVE,
        confirmation_prompt="permanently delete this directory and all its contents",
        audit_tag="dir_deletion",
        requires_explicit_consent=True
    ),

    # Code execution
    "execute_python_code": ToolSafetyMeta(
        level=SafetyLevel.DESTRUCTIVE,
        confirmation_prompt="execute Python code",
        audit_tag="code_execution",
        requires_explicit_consent=True
    ),
    "execute_javascript_code": ToolSafetyMeta(
        level=SafetyLevel.DESTRUCTIVE,
        confirmation_prompt="execute JavaScript code",
        audit_tag="code_execution",
        requires_explicit_consent=True
    ),

    # Desktop control
    "window_close": ToolSafetyMeta(
        level=SafetyLevel.MEDIUM,
        confirmation_prompt="close this window",
        audit_tag="window_close",
        requires_explicit_consent=False
    ),
    "app_kill": ToolSafetyMeta(
        level=SafetyLevel.DESTRUCTIVE,
        confirmation_prompt="terminate this process",
        audit_tag="process_kill",
        requires_explicit_consent=True
    ),

    # System operations
    "run_shell_command": ToolSafetyMeta(
        level=SafetyLevel.DESTRUCTIVE,
        confirmation_prompt="run this shell command",
        audit_tag="shell_command",
        requires_explicit_consent=True
    ),
}


# Confirmation phrases that indicate user consent
CONFIRMATION_PHRASES = [
    "yes proceed",
    "yes, proceed",
    "confirm",
    "do it",
    "go ahead",
    "execute",
    "run it",
    "yes",
]

# Cancellation phrases
CANCELLATION_PHRASES = [
    "no",
    "cancel",
    "stop",
    "abort",
    "don't",
    "wait",
    "hold on",
]


def normalize_phrase(phrase: str) -> str:
    """Normalize a phrase for comparison (lowercase, no punctuation)."""
    import re
    normalized = phrase.lower().strip()
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return normalized


async def require_voice_confirmation(
    context: RunContext,
    action_description: str,
    tool_name: str,
    timeout: int = 10
) -> bool:
    """
    Request voice confirmation from user for a potentially destructive operation.

    Args:
        context: The LiveKit run context
        action_description: Human-readable description of the action
        tool_name: Name of the tool being executed (for safety registry lookup)
        timeout: Seconds to wait for user response (default: 10)

    Returns:
        True if user explicitly confirms, False otherwise

    Example:
        confirmed = await require_voice_confirmation(
            context,
            "delete file test.txt from Desktop",
            "file_delete"
        )
    """
    try:
        # Get safety metadata
        safety_meta = TOOL_SAFETY_REGISTRY.get(tool_name)
        if not safety_meta:
            logger.warning(f"No safety metadata found for tool: {tool_name}")
            # Default to requiring confirmation for unknown tools
            safety_meta = ToolSafetyMeta(
                level=SafetyLevel.DESTRUCTIVE,
                confirmation_prompt="perform this action",
                audit_tag="unknown_operation"
            )

        # Check if confirmation is needed based on safety level
        if safety_meta.level == SafetyLevel.SAFE:
            logger.info(f"Tool {tool_name} is marked SAFE, no confirmation needed")
            return True

        # Build confirmation prompt
        prompt_text = (
            f"I need to {action_description}. "
            f"This is a {safety_meta.level.value} operation. "
            f"Please say 'yes, proceed' or 'confirm' to continue, or 'no' to cancel."
        )

        logger.info(f"Requesting confirmation for {tool_name}: {action_description}")
        logger.debug(f"Confirmation prompt: {prompt_text}")

        # TODO: Implement actual voice confirmation via LiveKit
        # For now, we'll use a simple input simulation
        # In production, this should:
        # 1. Use TTS to speak the prompt
        # 2. Listen for user voice response via STT
        # 3. Parse response and check against confirmation/cancellation phrases

        # Placeholder: Return True for testing
        # In production, replace with actual voice interaction
        logger.warning("Voice confirmation system not yet integrated with LiveKit - defaulting to DENY for safety")

        # For safety, default to False until voice system is integrated
        # This prevents accidental destructive operations
        return False

    except Exception as e:
        logger.error(f"Error in voice confirmation system: {e}", exc_info=True)
        # On error, deny for safety
        return False


def check_confirmation_phrase(user_response: str) -> Optional[bool]:
    """
    Check if user response is a confirmation or cancellation.

    Args:
        user_response: The user's spoken/typed response

    Returns:
        True if confirmed, False if cancelled, None if unclear
    """
    normalized = normalize_phrase(user_response)

    # Check for explicit confirmation
    for phrase in CONFIRMATION_PHRASES:
        if normalize_phrase(phrase) in normalized or normalized in normalize_phrase(phrase):
            return True

    # Check for explicit cancellation
    for phrase in CANCELLATION_PHRASES:
        if normalize_phrase(phrase) in normalized or normalized in normalize_phrase(phrase):
            return False

    # Unclear response
    return None


def is_system_path(path: str) -> bool:
    """
    Check if a path is in a critical system directory.

    Args:
        path: File or directory path

    Returns:
        True if path is in a system directory
    """
    import os
    path_lower = path.lower()

    system_dirs = [
        "c:\\windows",
        "c:\\program files",
        "c:\\program files (x86)",
        "c:\\programdata",
        "c:\\system32",
    ]

    for sys_dir in system_dirs:
        if path_lower.startswith(sys_dir):
            return True

    return False


def get_safety_level(tool_name: str) -> SafetyLevel:
    """
    Get the safety level for a tool.

    Args:
        tool_name: Name of the tool

    Returns:
        SafetyLevel enum value
    """
    meta = TOOL_SAFETY_REGISTRY.get(tool_name)
    if meta:
        return meta.level
    return SafetyLevel.DESTRUCTIVE  # Default to most restrictive


def register_tool_safety(
    tool_name: str,
    level: SafetyLevel,
    confirmation_prompt: str,
    audit_tag: str,
    requires_explicit_consent: bool = True
):
    """
    Register safety metadata for a new tool.

    Args:
        tool_name: Name of the tool
        level: Safety level
        confirmation_prompt: Human-readable action description
        audit_tag: Tag for audit logs
        requires_explicit_consent: Whether explicit confirmation is required
    """
    TOOL_SAFETY_REGISTRY[tool_name] = ToolSafetyMeta(
        level=level,
        confirmation_prompt=confirmation_prompt,
        audit_tag=audit_tag,
        requires_explicit_consent=requires_explicit_consent
    )
    logger.info(f"Registered safety metadata for {tool_name}: {level.value}")


# Example usage and testing
if __name__ == "__main__":
    # Test phrase matching
    print("Testing confirmation phrase matching:")
    test_phrases = [
        "yes, proceed",
        "confirm",
        "no thanks",
        "cancel that",
        "maybe later",
        "yes",
        "nope",
    ]

    for phrase in test_phrases:
        result = check_confirmation_phrase(phrase)
        print(f"  '{phrase}' -> {result}")

    # Test system path detection
    print("\nTesting system path detection:")
    test_paths = [
        "C:\\Windows\\System32\\test.dll",
        "C:\\Users\\John\\Documents\\file.txt",
        "C:\\Program Files\\App\\config.ini",
        "D:\\Projects\\code.py",
    ]

    for path in test_paths:
        is_sys = is_system_path(path)
        print(f"  '{path}' -> {'SYSTEM' if is_sys else 'USER'}")
