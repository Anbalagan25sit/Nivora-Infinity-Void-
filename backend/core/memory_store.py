import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Manages long-term, episodic memory for Nivora using SQLite.
    Stores facts, preferences, and context that persist across sessions.
    """

    def __init__(self, db_path: str = "data/memory/memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Episodic facts
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL DEFAULT 'default_user',
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Chat history (for recent context, bounded)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL DEFAULT 'default_user',
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info(f"Initialized MemoryStore at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing MemoryStore: {e}")

    def save_fact(self, key: str, value: str, user_id: str = "default_user"):
        """Save a persistent fact about the user (e.g. 'favorite_language', 'Python')."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute(
                    """
                    INSERT INTO facts (user_id, key, value, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                    """,
                    (user_id, key, value, now, now)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save fact: {e}")

    def get_fact(self, key: str, user_id: str = "default_user") -> Optional[str]:
        """Retrieve a specific fact by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM facts WHERE user_id = ? AND key = ?", (user_id, key))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Failed to get fact: {e}")
            return None

    def get_all_facts(self, user_id: str = "default_user") -> Dict[str, str]:
        """Retrieve all known facts for a user to inject into the system prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM facts WHERE user_id = ?", (user_id,))
                return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Failed to get all facts: {e}")
            return {}

    def delete_fact(self, key: str, user_id: str = "default_user"):
        """Remove a fact from memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM facts WHERE user_id = ? AND key = ?", (user_id, key))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to delete fact: {e}")

if __name__ == "__main__":
    # Test
    store = MemoryStore()
    store.save_fact("name", "Alex")
    print(store.get_all_facts())
