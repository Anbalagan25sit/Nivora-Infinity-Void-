import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class GoalManager:
    """
    Manages long-term goals and tasks in a local SQLite database.
    Allows Nivora to persist intentions across sessions.
    """

    def __init__(self, db_path: str = "data/memory/goals.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Goals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS goals (
                        id TEXT PRIMARY KEY,
                        description TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending', -- pending, active, completed, failed
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Tasks table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        goal_id TEXT NOT NULL,
                        description TEXT NOT NULL,
                        tool_name TEXT,
                        tool_args TEXT, -- JSON string
                        status TEXT NOT NULL DEFAULT 'pending', -- pending, active, completed, failed
                        result TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (goal_id) REFERENCES goals (id)
                    )
                ''')
                conn.commit()
                logger.info(f"Initialized GoalManager database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing GoalManager DB: {e}")

    def create_goal(self, description: str) -> str:
        """Create a new high-level goal."""
        goal_id = str(uuid.uuid4())
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO goals (id, description) VALUES (?, ?)",
                    (goal_id, description)
                )
                conn.commit()
            return goal_id
        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            return None

    def add_task(self, goal_id: str, description: str, tool_name: Optional[str] = None, tool_args: Optional[Dict] = None) -> str:
        """Add a sub-task to a goal."""
        task_id = str(uuid.uuid4())
        args_str = json.dumps(tool_args) if tool_args else "{}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (id, goal_id, description, tool_name, tool_args) VALUES (?, ?, ?, ?, ?)",
                    (task_id, goal_id, description, tool_name, args_str)
                )
                conn.commit()
            return task_id
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return None

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve tasks that need execution."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at ASC")
                rows = cursor.fetchall()

                tasks = []
                for row in rows:
                    task = dict(row)
                    task['tool_args'] = json.loads(task['tool_args']) if task['tool_args'] else {}
                    tasks.append(task)
                return tasks
        except Exception as e:
            logger.error(f"Failed to get pending tasks: {e}")
            return []

    def update_task_status(self, task_id: str, status: str, result: Optional[str] = None):
        """Update a task's status and optionally store its result."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                if result:
                    cursor.execute(
                        "UPDATE tasks SET status = ?, result = ?, updated_at = ? WHERE id = ?",
                        (status, result, now, task_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                        (status, now, task_id)
                    )

                # Check if all tasks for the parent goal are completed
                cursor.execute("SELECT goal_id FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if row:
                    goal_id = row[0]
                    self._check_and_update_goal_status(goal_id, conn)

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")

    def _check_and_update_goal_status(self, goal_id: str, conn: sqlite3.Connection):
        """Internal helper to mark a goal completed if all its tasks are done."""
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tasks WHERE goal_id = ?", (goal_id,))
        statuses = [row[0] for row in cursor.fetchall()]

        if all(s == 'completed' for s in statuses):
            cursor.execute("UPDATE goals SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (goal_id,))
        elif any(s == 'failed' for s in statuses):
            cursor.execute("UPDATE goals SET status = 'failed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (goal_id,))
        elif any(s == 'active' for s in statuses):
            cursor.execute("UPDATE goals SET status = 'active', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (goal_id,))

    def get_goal_summary(self, goal_id: str) -> Dict[str, Any]:
        """Get the full state of a goal and its tasks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
                goal_row = cursor.fetchone()
                if not goal_row:
                    return {}

                goal = dict(goal_row)

                cursor.execute("SELECT * FROM tasks WHERE goal_id = ?", (goal_id,))
                tasks = []
                for row in cursor.fetchall():
                    task = dict(row)
                    task['tool_args'] = json.loads(task['tool_args']) if task['tool_args'] else {}
                    tasks.append(task)

                goal['tasks'] = tasks
                return goal
        except Exception as e:
            logger.error(f"Failed to get goal summary: {e}")
            return {}

    def get_all_active_goals(self) -> List[Dict[str, Any]]:
        """Get all non-completed/failed goals."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM goals WHERE status IN ('pending', 'active')")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get active goals: {e}")
            return []
