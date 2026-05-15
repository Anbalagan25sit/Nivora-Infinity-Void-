"""
Audit Logging System for Nivora Desktop Automation

This module provides structured logging for all tool executions,
especially destructive operations, for security and debugging purposes.

All audit logs are written to audit_logs/ directory in JSON Lines format.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logger for tracking all tool executions.

    Logs are written to: audit_logs/YYYY-MM-DD.jsonl
    Each line is a JSON object with structured data.
    """

    def __init__(self, log_dir: str = "data/memory/audit_logs"):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory to store audit logs (default: audit_logs/)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        logger.info(f"Audit logger initialized, logs directory: {self.log_dir.absolute()}")

    def _get_log_file(self) -> Path:
        """Get the log file path for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"{today}.jsonl"

    def log_tool_execution(
        self,
        tool_name: str,
        params: Dict[str, Any],
        user_confirmed: bool,
        result: str,
        session_id: str,
        agent_name: str = "Nivora",
        confirmation_phrase: Optional[str] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> None:
        """
        Log a tool execution to the audit trail.

        Args:
            tool_name: Name of the tool executed
            params: Parameters passed to the tool
            user_confirmed: Whether user explicitly confirmed the action
            result: Result status (success/failure)
            session_id: LiveKit session/room ID
            agent_name: Name of the agent (default: Nivora)
            confirmation_phrase: Exact phrase user said to confirm (if applicable)
            error: Error message if execution failed
            duration_ms: Execution time in milliseconds
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "agent": agent_name,
                "tool": tool_name,
                "params": params,
                "user_confirmed": user_confirmed,
                "confirmation_phrase": confirmation_phrase,
                "result": result,
                "error": error,
                "duration_ms": duration_ms,
            }

            log_file = self._get_log_file()

            # Append to today's log file (JSON Lines format)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            logger.info(
                f"Audit log: {tool_name} | confirmed={user_confirmed} | "
                f"result={result} | session={session_id}"
            )

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}", exc_info=True)

    def log_safety_denial(
        self,
        tool_name: str,
        params: Dict[str, Any],
        reason: str,
        session_id: str,
        agent_name: str = "Nivora"
    ) -> None:
        """
        Log when a tool execution was denied by the safety system.

        Args:
            tool_name: Name of the tool that was denied
            params: Parameters that would have been passed
            reason: Reason for denial
            session_id: LiveKit session/room ID
            agent_name: Name of the agent
        """
        self.log_tool_execution(
            tool_name=tool_name,
            params=params,
            user_confirmed=False,
            result="denied",
            session_id=session_id,
            agent_name=agent_name,
            error=reason
        )

    def get_recent_logs(self, limit: int = 100) -> list[Dict[str, Any]]:
        """
        Retrieve recent audit log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of log entries (most recent first)
        """
        try:
            log_file = self._get_log_file()

            if not log_file.exists():
                return []

            entries = []
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            # Return most recent first
            return list(reversed(entries[-limit:]))

        except Exception as e:
            logger.error(f"Failed to read audit logs: {e}", exc_info=True)
            return []

    def search_logs(
        self,
        tool_name: Optional[str] = None,
        session_id: Optional[str] = None,
        user_confirmed: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[Dict[str, Any]]:
        """
        Search audit logs with filters.

        Args:
            tool_name: Filter by tool name
            session_id: Filter by session ID
            user_confirmed: Filter by confirmation status
            start_date: Filter by start datetime
            end_date: Filter by end datetime

        Returns:
            List of matching log entries
        """
        try:
            matching_entries = []

            # Iterate through all log files in date range
            for log_file in sorted(self.log_dir.glob("*.jsonl")):
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line)

                            # Apply filters
                            if tool_name and entry.get("tool") != tool_name:
                                continue

                            if session_id and entry.get("session_id") != session_id:
                                continue

                            if user_confirmed is not None and entry.get("user_confirmed") != user_confirmed:
                                continue

                            entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                            if start_date and entry_time < start_date:
                                continue
                            if end_date and entry_time > end_date:
                                continue

                            matching_entries.append(entry)

                        except (json.JSONDecodeError, ValueError):
                            continue

            return matching_entries

        except Exception as e:
            logger.error(f"Failed to search audit logs: {e}", exc_info=True)
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about tool usage from audit logs.

        Returns:
            Dictionary with usage statistics
        """
        try:
            logs = self.get_recent_logs(limit=1000)

            stats = {
                "total_executions": len(logs),
                "confirmed_executions": sum(1 for log in logs if log.get("user_confirmed")),
                "denied_executions": sum(1 for log in logs if log.get("result") == "denied"),
                "successful_executions": sum(1 for log in logs if log.get("result") == "success"),
                "failed_executions": sum(1 for log in logs if log.get("error") is not None),
                "tools_used": {},
                "sessions": set(),
            }

            for log in logs:
                tool = log.get("tool", "unknown")
                stats["tools_used"][tool] = stats["tools_used"].get(tool, 0) + 1
                if log.get("session_id"):
                    stats["sessions"].add(log.get("session_id"))

            stats["unique_sessions"] = len(stats["sessions"])
            stats["sessions"] = list(stats["sessions"])  # Convert set to list for JSON

            return stats

        except Exception as e:
            logger.error(f"Failed to generate statistics: {e}", exc_info=True)
            return {}


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """
    Get the global audit logger instance (singleton pattern).

    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience functions for direct logging
def log_tool_execution(*args, **kwargs):
    """Convenience function to log tool execution."""
    get_audit_logger().log_tool_execution(*args, **kwargs)


def log_safety_denial(*args, **kwargs):
    """Convenience function to log safety denial."""
    get_audit_logger().log_safety_denial(*args, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    print("Testing Audit Logger...")

    # Create logger
    logger_instance = AuditLogger(log_dir="test_audit_logs")

    # Log some test executions
    print("\n1. Logging successful file read (no confirmation needed):")
    logger_instance.log_tool_execution(
        tool_name="file_read",
        params={"path": "/home/user/test.txt"},
        user_confirmed=False,  # No confirmation needed for safe operations
        result="success",
        session_id="test-session-001",
        duration_ms=150
    )

    print("\n2. Logging confirmed file deletion:")
    logger_instance.log_tool_execution(
        tool_name="file_delete",
        params={"path": "/home/user/old_file.txt"},
        user_confirmed=True,
        confirmation_phrase="yes, proceed",
        result="success",
        session_id="test-session-001",
        duration_ms=50
    )

    print("\n3. Logging denied code execution:")
    logger_instance.log_safety_denial(
        tool_name="execute_python_code",
        params={"code": "print('hello')"},
        reason="User cancelled confirmation",
        session_id="test-session-001"
    )

    print("\n4. Logging failed operation:")
    logger_instance.log_tool_execution(
        tool_name="file_write",
        params={"path": "/protected/file.txt", "content": "data"},
        user_confirmed=True,
        confirmation_phrase="confirm",
        result="failure",
        session_id="test-session-002",
        error="Permission denied",
        duration_ms=25
    )

    # Retrieve and display logs
    print("\n5. Recent log entries:")
    recent = logger_instance.get_recent_logs(limit=10)
    for i, entry in enumerate(recent, 1):
        print(f"\n   Entry {i}:")
        print(f"     Tool: {entry['tool']}")
        print(f"     Confirmed: {entry['user_confirmed']}")
        print(f"     Result: {entry['result']}")
        if entry.get('error'):
            print(f"     Error: {entry['error']}")

    # Get statistics
    print("\n6. Usage statistics:")
    stats = logger_instance.get_statistics()
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Confirmed: {stats['confirmed_executions']}")
    print(f"   Denied: {stats['denied_executions']}")
    print(f"   Successful: {stats['successful_executions']}")
    print(f"   Failed: {stats['failed_executions']}")
    print(f"   Tools used: {stats['tools_used']}")

    print("\nAudit logs written to: test_audit_logs/")
    print("Audit logger test complete!")
