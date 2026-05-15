"""
Browser-Use Agent for E-Box Differential Equations
Autonomous agent using browser-use library to solve problems in i-Learn and i-Analyse sections
https://github.com/browser-use/browser-use
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# E-Box credentials
EBOX_USERNAME = os.getenv("EBOX_USERNAME", "SIT25CS170")
EBOX_PASSWORD = os.getenv("EBOX_PASSWORD", "SIT25CS170")
EBOX_LOGIN_URL = "https://pro.e-box.co.in/login"


@dataclass
class EBoxConfig:
    """Configuration for E-Box automation"""
    course_name: str = "Differential Equations And Complex Analysis"
    sections: list = None  # Default to ["i-Learn", "i-Analyse"]
    headless: bool = False  # Set to True for production

    def __post_init__(self):
        if self.sections is None:
            self.sections = ["i-Learn", "i-Analyse"]


def _init_llm():
    """Initialize the LLM for the agent"""
    # Try AWS Bedrock Nova Pro FIRST (already configured for Nivora!)
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        logger.info("[BrowserAgent] Using AWS Bedrock Nova Pro")
        try:
            from langchain_aws import ChatBedrockConverse
            from browser_use.llm.base import BaseChatModel
            from browser_use.llm.messages import (
                AssistantMessage,
                SystemMessage,
                UserMessage,
                ContentPartTextParam,
                ContentPartImageParam,
            )
            from typing import Union, Sequence

            # Create a proper BaseChatModel implementation for AWS Bedrock
            class AWSBedrockLLM:
                """AWS Bedrock LLM implementation for browser-use"""

                _verified_api_keys: bool = True

                def __init__(self, model_id: str, region: str, temperature: float = 0.7, max_tokens: int = 4096):
                    self._model_id = model_id
                    self._region = region
                    self._temperature = temperature
                    self._max_tokens = max_tokens
                    self._llm = ChatBedrockConverse(
                        model=model_id,
                        region_name=region,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    # browser-use expects this attribute
                    self.model = model_id

                @property
                def provider(self) -> str:
                    return 'aws-bedrock'

                @property
                def name(self) -> str:
                    return f"aws-bedrock/{self._model_id}"

                @property
                def model_name(self) -> str:
                    return self._model_id

                async def ainvoke(
                    self,
                    messages: Sequence[Union[SystemMessage, UserMessage, AssistantMessage]],
                    output_format=None,
                    **kwargs
                ):
                    """Invoke the LLM with messages and return response"""
                    print(f"[DEBUG] ainvoke called with {len(messages)} messages, output_format={output_format}")
                    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage as LCSystemMessage

                    # Check if structured output is requested
                    if output_format is not None:
                        print(f"[DEBUG] Structured output requested: {output_format}")
                        # Use the structured output approach
                        return await self._handle_structured_output(messages, output_format, **kwargs)

                    # Filter out kwargs that LangChain Bedrock doesn't support
                    unsupported_keys = ['sessionId', 'session_id']
                    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in unsupported_keys}
                    print(f"[DEBUG] filtered_kwargs: {filtered_kwargs.keys()}")

                    # Convert browser-use messages to LangChain format
                    lc_messages = []
                    for msg in messages:
                        if isinstance(msg, SystemMessage):
                            lc_messages.append(LCSystemMessage(content=msg.content))
                        elif isinstance(msg, UserMessage):
                            # Handle multi-modal content
                            content_parts = []
                            for part in msg.content:
                                if isinstance(part, ContentPartTextParam):
                                    content_parts.append({"type": "text", "text": part.text})
                                elif isinstance(part, ContentPartImageParam):
                                    if hasattr(part, 'image_url') and part.image_url:
                                        url = part.image_url.url if hasattr(part.image_url, 'url') else str(part.image_url)
                                        content_parts.append({
                                            "type": "image_url",
                                            "image_url": {"url": url}
                                        })
                            if len(content_parts) == 1 and content_parts[0]["type"] == "text":
                                lc_messages.append(HumanMessage(content=content_parts[0]["text"]))
                            else:
                                lc_messages.append(HumanMessage(content=content_parts))
                        elif isinstance(msg, AssistantMessage):
                            text_content = ""
                            for part in msg.content:
                                if isinstance(part, ContentPartTextParam):
                                    text_content += part.text
                                elif hasattr(part, 'text'):
                                    text_content += part.text
                            lc_messages.append(AIMessage(content=text_content))

                    # Call LangChain model
                    response = await self._llm.ainvoke(lc_messages, **filtered_kwargs)

                    # Convert response to browser-use format
                    from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage

                    assistant_msg = AssistantMessage(content=[ContentPartTextParam(type="text", text=response.content)])

                    # Create usage info for token tracking
                    usage_info = getattr(response, 'usage_metadata', None)
                    if usage_info:
                        usage = ChatInvokeUsage(
                            prompt_tokens=usage_info.get('input_tokens', 0),
                            prompt_cached_tokens=usage_info.get('input_cached_tokens'),
                            prompt_cache_creation_tokens=None,
                            prompt_image_tokens=None,
                            completion_tokens=usage_info.get('output_tokens', 0),
                            total_tokens=usage_info.get('total_tokens', 0)
                        )
                    else:
                        # Fallback: estimate token usage
                        input_text = ' '.join(str(msg.content) for msg in messages)
                        prompt_tokens = int(len(input_text.split()) * 1.3)  # rough estimate
                        completion_tokens = int(len(response.content.split()) * 1.3)
                        usage = ChatInvokeUsage(
                            prompt_tokens=prompt_tokens,
                            prompt_cached_tokens=None,
                            prompt_cache_creation_tokens=None,
                            prompt_image_tokens=None,
                            completion_tokens=completion_tokens,
                            total_tokens=prompt_tokens + completion_tokens
                        )

                    completion = ChatInvokeCompletion(
                        completion=assistant_msg,
                        thinking=None,
                        redacted_thinking=None,
                        usage=usage,
                        stop_reason=None
                    )
                    print(f"[DEBUG] Returning completion: {type(completion)}")
                    print(f"[DEBUG] completion.completion: {type(completion.completion)}")
                    print(f"[DEBUG] completion.completion.content: {completion.completion.content}")

                    return completion

                async def _handle_structured_output(self, messages, output_format, **kwargs):
                    """Handle structured output requests from browser-use"""
                    print(f"[DEBUG] Handling structured output for format: {output_format}")

                    # Import required classes
                    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage as LCSystemMessage
                    from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage
                    import json

                    # Convert messages to LangChain format
                    lc_messages = []
                    for msg in messages:
                        if isinstance(msg, SystemMessage):
                            lc_messages.append(LCSystemMessage(content=msg.content))
                        elif isinstance(msg, UserMessage):
                            content_parts = []
                            for part in msg.content:
                                if isinstance(part, ContentPartTextParam):
                                    content_parts.append({"type": "text", "text": part.text})
                                elif isinstance(part, ContentPartImageParam):
                                    if hasattr(part, 'image_url') and part.image_url:
                                        url = part.image_url.url if hasattr(part.image_url, 'url') else str(part.image_url)
                                        content_parts.append({
                                            "type": "image_url",
                                            "image_url": {"url": url}
                                        })
                            if len(content_parts) == 1 and content_parts[0]["type"] == "text":
                                lc_messages.append(HumanMessage(content=content_parts[0]["text"]))
                            else:
                                lc_messages.append(HumanMessage(content=content_parts))
                        elif isinstance(msg, AssistantMessage):
                            text_content = ""
                            for part in msg.content:
                                if isinstance(part, ContentPartTextParam):
                                    text_content += part.text
                                elif hasattr(part, 'text'):
                                    text_content += part.text
                            lc_messages.append(AIMessage(content=text_content))

                    # Filter kwargs
                    unsupported_keys = ['sessionId', 'session_id']
                    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in unsupported_keys}

                    try:
                        # Use LangChain's with_structured_output to get properly formatted response
                        structured_llm = self._llm.with_structured_output(output_format)
                        structured_response = await structured_llm.ainvoke(lc_messages, **filtered_kwargs)

                        print(f"[DEBUG] Structured response type: {type(structured_response)}")
                        print(f"[DEBUG] Structured response: {structured_response}")

                        # The structured response should already be in the correct format
                        # We need to wrap it in a ChatInvokeCompletion but NOT as AssistantMessage
                        # because browser-use expects the raw structured object

                        # Create basic usage tracking (estimated)
                        usage = ChatInvokeUsage(
                            prompt_tokens=sum(len(str(msg.content).split()) for msg in messages),
                            prompt_cached_tokens=None,
                            prompt_cache_creation_tokens=None,
                            prompt_image_tokens=None,
                            completion_tokens=50,  # Rough estimate for structured output
                            total_tokens=sum(len(str(msg.content).split()) for msg in messages) + 50
                        )

                        # Return the structured response directly - browser-use expects this format
                        completion = ChatInvokeCompletion(
                            completion=structured_response,  # This should be the AgentOutput object
                            thinking=None,
                            redacted_thinking=None,
                            usage=usage,
                            stop_reason=None
                        )

                        print(f"[DEBUG] Returning structured completion: {type(completion)}")
                        print(f"[DEBUG] completion.completion: {type(completion.completion)}")

                        return completion

                    except Exception as e:
                        print(f"[DEBUG] Structured output failed: {e}")
                        import traceback
                        traceback.print_exc()

                        # Fallback: try to parse manually or return a simple action
                        # This is a last resort if AWS Bedrock doesn't support the structured format
                        from browser_use.agent.views import AgentOutput
                        from browser_use.tools.registry.views import ActionModel

                        # Create a simple fallback action (navigate to the E-Box login page)
                        fallback_action = ActionModel()

                        fallback_output = AgentOutput(
                            thinking="Starting E-Box automation task",
                            next_goal="Navigate to E-Box login page",
                            action=[fallback_action]
                        )

                        usage = ChatInvokeUsage(
                            prompt_tokens=sum(len(str(msg.content).split()) for msg in messages),
                            prompt_cached_tokens=None,
                            prompt_cache_creation_tokens=None,
                            prompt_image_tokens=None,
                            completion_tokens=50,
                            total_tokens=sum(len(str(msg.content).split()) for msg in messages) + 50
                        )

                        completion = ChatInvokeCompletion(
                            completion=fallback_output,
                            thinking=None,
                            redacted_thinking=None,
                            usage=usage,
                            stop_reason=None
                        )

                        return completion

                def bind_tools(self, *args, **kwargs):
                    """Bind tools to the LLM for browser actions"""
                    print(f"[DEBUG] bind_tools called with {len(args)} args")
                    bound_llm = self._llm.bind_tools(*args, **kwargs)

                    # Create a new wrapper instance with the bound LLM
                    wrapper = AWSBedrockLLM.__new__(AWSBedrockLLM)
                    wrapper._llm = bound_llm
                    wrapper._model_id = self._model_id
                    wrapper._region = self._region
                    wrapper._temperature = self._temperature
                    wrapper._max_tokens = self._max_tokens
                    wrapper.model = self._model_id

                    return wrapper

                def with_structured_output(self, *args, **kwargs):
                    """Support structured output if needed"""
                    structured_llm = self._llm.with_structured_output(*args, **kwargs)

                    # Create a new wrapper instance
                    wrapper = AWSBedrockLLM.__new__(AWSBedrockLLM)
                    wrapper._llm = structured_llm
                    wrapper._model_id = self._model_id
                    wrapper._region = self._region
                    wrapper._temperature = self._temperature
                    wrapper._max_tokens = self._max_tokens
                    wrapper.model = self._model_id

                    return wrapper

            model_name = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0")
            bedrock_llm = AWSBedrockLLM(
                model_id=model_name,
                region=os.getenv("AWS_REGION", "us-east-1"),
                temperature=0.7,
                max_tokens=4096,
            )
            print(f"[DEBUG] Created AWSBedrockLLM: {type(bedrock_llm)}")
            print(f"[DEBUG] LLM methods: {[m for m in dir(bedrock_llm) if not m.startswith('_')]}")
            return bedrock_llm
        except ImportError as e:
            logger.warning(f"[BrowserAgent] AWS Bedrock setup failed: {e}")
            import traceback
            traceback.print_exc()
            logger.info("[BrowserAgent] Falling back to Anthropic/OpenAI")
        except Exception as e:
            logger.warning(f"[BrowserAgent] AWS Bedrock failed: {e}")
            import traceback
            traceback.print_exc()
            logger.info("[BrowserAgent] Falling back to Anthropic/OpenAI")

    # Fallback to Anthropic (if AWS not configured)
    if os.getenv("ANTHROPIC_API_KEY"):
        logger.info("[BrowserAgent] Using Anthropic Claude")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    # Fallback to OpenAI
    elif os.getenv("OPENAI_API_KEY"):
        logger.info("[BrowserAgent] Using OpenAI GPT-4")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    # No LLM configured
    else:
        raise ValueError(
            "No LLM configured! Please set one of:\n"
            "  - AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (for Bedrock Nova Pro)\n"
            "  - ANTHROPIC_API_KEY (for Claude)\n"
            "  - OPENAI_API_KEY (for GPT-4)"
        )


class EBoxBrowserAgent:
    """Browser-use agent for autonomous E-Box problem solving"""

    def __init__(self, config: Optional[EBoxConfig] = None):
        self.config = config or EBoxConfig()
        self.browser = None
        self.agent = None
        # We don't initialize local LLM anymore since we're using cloud SDK

    async def solve_differential_equations_course(self) -> Dict[str, Any]:
        """
        Main entry point - solve all differential equation problems in i-Learn and i-Analyse
        """
        try:
            # Create BrowserUse client with cloud SDK
            from browser_use_sdk.v3 import BrowserUse

            client = BrowserUse(api_key="bu_BHR3by2HGWykzuWlDuCkswnrf2YzRK0DMiDmX33a3jg")

            # Create comprehensive task for the agent
            task = self._build_comprehensive_task()

            logger.info("[BrowserAgent] Starting autonomous problem-solving session via Cloud API...")

            # Run the agent - it will autonomously navigate and solve problems
            result = client.run(
                task,
                model="bu-ultra",
                profile_id="bd8025a9-6055-4b46-970f-460cd32dfea9",
                workspace_id="88fd6389-84d2-4830-ba32-c1c1694d893e",
                proxy_country_code="us",
            )

            return {
                "success": True,
                "message": "Agent completed the task",
                "result": str(result.output),
                "actions_taken": "unknown"
            }

        except Exception as e:
            logger.error(f"[BrowserAgent] Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass

    def _build_comprehensive_task(self) -> str:
        """
        Build comprehensive task description for the browser-use agent
        The agent will use this to autonomously navigate and solve problems
        """
        task = f"""
your goal is to open goto  https://pro.e-box.co.in/login , finiish course : programming python and finish last three units  and work backward username and password :  {EBOX_USERNAME}
"""
        return task

    async def solve_specific_section(self, topic_name: str, section: str) -> Dict[str, Any]:
        """
        Solve problems in a specific topic and section

        Args:
            topic_name: e.g., "Solution of Ordinary Differential Equations"
            section: e.g., "i-Learn" or "i-Analyse"
        """
        try:
            # Create BrowserUse client with cloud SDK
            from browser_use_sdk.v3 import BrowserUse

            client = BrowserUse(api_key="bu_BHR3by2HGWykzuWlDuCkswnrf2YzRK0DMiDmX33a3jg")

            logger.info(f"[BrowserAgent] Starting autonomous problem-solving session for {topic_name}/{section} via Cloud API...")

            # We use the bu-ultra model for best results
            task_prompt = f"""
Login to E-Box ({EBOX_LOGIN_URL}) with username {EBOX_USERNAME} and password {EBOX_PASSWORD}.

Navigate to course: {self.config.course_name}

Click on topic: {topic_name}

Click on section tab: {section}

Solve all problems in this section. For differential equation problems:
- Read the problem carefully
- Apply appropriate solution method
- Verify solution satisfies the equation
- Submit the answer

Complete all problems and report results.
"""
            result = client.run(
                task_prompt,
                model="bu-ultra",
                profile_id="bd8025a9-6055-4b46-970f-460cd32dfea9",
                workspace_id="88fd6389-84d2-4830-ba32-c1c1694d893e",
                proxy_country_code="us",
            )

            return {
                "success": True,
                "topic": topic_name,
                "section": section,
                "result": str(result.output)
            }

        except Exception as e:
            logger.error(f"[BrowserAgent] Error solving {topic_name}/{section}: {e}")
            return {
                "success": False,
                "topic": topic_name,
                "section": section,
                "error": str(e)
            }
        finally:
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass


async def main():
    """Test the browser-use agent"""
    config = EBoxConfig(
        course_name="Differential Equations And Complex Analysis",
        sections=["i-Learn", "i-Analyse"],
        headless=False  # Show browser for debugging
    )

    agent = EBoxBrowserAgent(config)
    result = await agent.solve_differential_equations_course()

    print("\n" + "="*80)
    print("AGENT EXECUTION RESULT")
    print("="*80)
    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Message: {result.get('message')}")
        print(f"Actions taken: {result.get('actions_taken')}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*80)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main())
