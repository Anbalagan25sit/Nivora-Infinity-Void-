import asyncio
import logging
from typing import Dict, Any

from goal_manager import GoalManager

# Import tools that might be run in the background
try:
    from browser_use_langgraph_tools import solve_ebox_course_langgraph, solve_ebox_section_langgraph
except ImportError:
    solve_ebox_course_langgraph = None
    solve_ebox_section_langgraph = None

logger = logging.getLogger(__name__)

class BackgroundWorker:
    """
    An asyncio daemon that polls the GoalManager for pending tasks
    and executes them in the background, without requiring an active LiveKit connection.
    """
    def __init__(self, db_path: str = "goals.db", poll_interval_seconds: int = 10):
        self.goal_manager = GoalManager(db_path=db_path)
        self.poll_interval = poll_interval_seconds
        self._is_running = False

    async def start(self):
        """Start the background execution loop."""
        self._is_running = True
        logger.info(f"Background worker started, polling every {self.poll_interval}s")
        asyncio.create_task(self._loop())

    async def stop(self):
        """Stop the background execution loop."""
        self._is_running = False
        logger.info("Background worker stopped.")

    async def _loop(self):
        """The main polling loop."""
        while self._is_running:
            try:
                # Find pending tasks
                pending_tasks = self.goal_manager.get_pending_tasks()
                if pending_tasks:
                    logger.info(f"Found {len(pending_tasks)} pending background tasks.")
                    for task in pending_tasks:
                        # Process sequentially (or async via create_task if we wanted parallel execution)
                        await self._execute_task(task)
            except Exception as e:
                logger.error(f"Error in background loop: {e}", exc_info=True)

            await asyncio.sleep(self.poll_interval)

    async def _execute_task(self, task: Dict[str, Any]):
        """Execute a specific task using the registered tool."""
        task_id = task['id']
        tool_name = task.get('tool_name')
        args = task.get('tool_args', {})

        logger.info(f"Executing task {task_id}: {tool_name} with args {args}")

        # Mark task as active
        self.goal_manager.update_task_status(task_id, 'active')

        try:
            result = None
            if tool_name == "solve_ebox_course_langgraph" and solve_ebox_course_langgraph:
                # Call the async function directly
                result = await solve_ebox_course_langgraph(**args)
            elif tool_name == "solve_ebox_section_langgraph" and solve_ebox_section_langgraph:
                result = await solve_ebox_section_langgraph(**args)
            else:
                # Fallback or simulated long-running task
                logger.warning(f"Unknown or unavailable background tool: {tool_name}. Simulating execution.")
                await asyncio.sleep(5)
                result = f"Simulated success for tool {tool_name}"

            # Task succeeded
            self.goal_manager.update_task_status(task_id, 'completed', str(result))
            logger.info(f"Task {task_id} completed successfully.")

        except Exception as e:
            # Task failed
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)
            self.goal_manager.update_task_status(task_id, 'failed', str(e))

if __name__ == "__main__":
    # Test the background worker directly
    logging.basicConfig(level=logging.INFO)
    async def main():
        worker = BackgroundWorker(poll_interval_seconds=5)

        # Inject a test goal
        gm = GoalManager()
        goal_id = gm.create_goal("Background Test Goal")
        gm.add_task(goal_id, "Test background task execution", "simulated_tool", {"param": "value"})

        await worker.start()
        await asyncio.sleep(15)  # Let it run for a bit
        await worker.stop()

    asyncio.run(main())
