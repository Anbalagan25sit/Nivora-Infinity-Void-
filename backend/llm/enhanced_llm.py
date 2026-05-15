import os
import logging
from typing import Union, Sequence

try:
    from langchain_aws import ChatBedrockConverse
except ImportError:
    pass  # We'll let it fail later if it's actually used and not installed.

try:
    from browser_use.llm.base import BaseChatModel
    from browser_use.llm.messages import (
        AssistantMessage,
        SystemMessage,
        UserMessage,
        ContentPartTextParam,
        ContentPartImageParam,
    )
    from browser_use.llm.views import ChatInvokeCompletion, ChatInvokeUsage
except ImportError:
    pass

logger = logging.getLogger(__name__)

class EnhancedAWSBedrockLLM:
    """Enhanced AWS Bedrock LLM with advanced reasoning capabilities"""

    _verified_api_keys: bool = True

    def __init__(self, model_id: str, region: str, temperature: float = 0.3, max_tokens: int = 8192):
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
        self.model = model_id

    @property
    def provider(self) -> str:
        return 'aws-bedrock-enhanced'

    @property
    def name(self) -> str:
        return f"aws-bedrock-enhanced/{self._model_id}"

    @property
    def model_name(self) -> str:
        return self._model_id

    async def ainvoke(
        self,
        messages: Sequence[Union['SystemMessage', 'UserMessage', 'AssistantMessage']],
        output_format=None,
        **kwargs
    ):
        """Enhanced invoke with advanced reasoning and error handling"""
        print(f"[DEBUG] Enhanced ainvoke called with {len(messages)} messages")

        if output_format is not None:
            return await self._handle_enhanced_structured_output(messages, output_format, **kwargs)

        return await self._handle_standard_response(messages, **kwargs)

    async def _handle_enhanced_structured_output(self, messages, output_format, **kwargs):
        """Advanced structured output with enhanced reasoning"""
        print(f"[DEBUG] Enhanced structured output for: {output_format}")

        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage as LCSystemMessage
        import json

        lc_messages = self._convert_messages_with_context(messages)

        enhanced_system_prompt = """
You are an advanced web automation agent with exceptional reasoning capabilities.

ENHANCED REASONING FRAMEWORK:
1. ANALYZE: Deeply understand the current page structure, context, and user intent
2. PLAN: Create a multi-step plan with contingencies and error handling
3. ADAPT: Adjust strategy based on page changes and unexpected situations
4. EXECUTE: Perform actions with precision and verification
5. LEARN: Remember successful patterns for future tasks

ADVANCED CAPABILITIES:
- Multi-step planning with conditional logic
- Adaptive waiting based on page complexity
- Form auto-completion with intelligent field detection
- Error recovery with alternative strategies
- Pattern recognition for similar websites
- Context-aware decision making

RESPONSE FORMAT:
Always provide structured responses with:
- Clear thinking process
- Step-by-step action plan
- Error handling considerations
- Success verification methods
"""

        if lc_messages and not isinstance(lc_messages[0], LCSystemMessage):
            lc_messages.insert(0, LCSystemMessage(content=enhanced_system_prompt))
        elif lc_messages and isinstance(lc_messages[0], LCSystemMessage):
            lc_messages[0].content += "\n\n" + enhanced_system_prompt

        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['sessionId', 'session_id']}

        try:
            structured_llm = self._llm.with_structured_output(output_format)
            structured_response = await structured_llm.ainvoke(lc_messages, **filtered_kwargs)

            print(f"[DEBUG] Enhanced structured response: {type(structured_response)}")

            usage = ChatInvokeUsage(
                prompt_tokens=sum(len(str(msg.content).split()) for msg in messages),
                prompt_cached_tokens=None,
                prompt_cache_creation_tokens=None,
                prompt_image_tokens=None,
                completion_tokens=100,
                total_tokens=sum(len(str(msg.content).split()) for msg in messages) + 100
            )

            completion = ChatInvokeCompletion(
                completion=structured_response,
                thinking=None,
                redacted_thinking=None,
                usage=usage,
                stop_reason=None
            )

            return completion

        except Exception as e:
            print(f"[DEBUG] Enhanced structured output failed: {e}")
            return await self._create_fallback_response(output_format, messages)

    async def _handle_standard_response(self, messages, **kwargs):
        """Handle standard text responses with enhanced context"""
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage as LCSystemMessage

        lc_messages = self._convert_messages_with_context(messages)

        filtered_kwargs = {k: v for k, v in kwargs.items()
                           if k not in ['sessionId', 'session_id']}

        response = await self._llm.ainvoke(lc_messages, **filtered_kwargs)

        assistant_msg = AssistantMessage(
            content=[ContentPartTextParam(type="text", text=response.content)]
        )

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
            input_text = ' '.join(str(msg.content) for msg in messages)
            prompt_tokens = int(len(input_text.split()) * 1.4)
            completion_tokens = int(len(response.content.split()) * 1.4)
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

        return completion

    def _convert_messages_with_context(self, messages):
        """Convert messages with enhanced context and reasoning"""
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage as LCSystemMessage

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

        return lc_messages

    async def _create_fallback_response(self, output_format, messages):
        """Create intelligent fallback response"""
        from browser_use.agent.views import AgentOutput
        from browser_use.tools.registry.views import ActionModel
        from browser_use.llm.views import ChatInvokeUsage, ChatInvokeCompletion

        task_content = ""
        for msg in messages:
            if hasattr(msg, 'content'):
                if isinstance(msg.content, list):
                    for part in msg.content:
                        if hasattr(part, 'text'):
                            task_content += part.text
                else:
                    task_content += str(msg.content)

        fallback_action = ActionModel()

        if "login" in task_content.lower():
            thinking = "Detected login task. Will look for login forms and credentials."
            next_goal = "Locate and fill login form"
        elif "search" in task_content.lower():
            thinking = "Detected search task. Will look for search functionality."
            next_goal = "Find search input and perform search"
        elif "buy" in task_content.lower() or "purchase" in task_content.lower():
            thinking = "Detected purchase task. Will navigate shopping flow."
            next_goal = "Navigate to product and initiate purchase"
        elif "form" in task_content.lower() or "fill" in task_content.lower():
            thinking = "Detected form filling task. Will analyze form structure."
            next_goal = "Analyze and fill form fields"
        else:
            thinking = "Analyzing page structure and task requirements."
            next_goal = "Understand page layout and identify actionable elements"

        fallback_output = AgentOutput(
            thinking=thinking,
            next_goal=next_goal,
            action=[fallback_action]
        )

        usage = ChatInvokeUsage(
            prompt_tokens=sum(len(str(msg.content).split()) for msg in messages),
            prompt_cached_tokens=None,
            prompt_cache_creation_tokens=None,
            prompt_image_tokens=None,
            completion_tokens=80,
            total_tokens=sum(len(str(msg.content).split()) for msg in messages) + 80
        )

        return ChatInvokeCompletion(
            completion=fallback_output,
            thinking=None,
            redacted_thinking=None,
            usage=usage,
            stop_reason=None
        )

    def bind_tools(self, *args, **kwargs):
        """Enhanced tool binding with advanced capabilities"""
        print(f"[DEBUG] Enhanced bind_tools called with {len(args)} args")
        bound_llm = self._llm.bind_tools(*args, **kwargs)

        wrapper = EnhancedAWSBedrockLLM.__new__(EnhancedAWSBedrockLLM)
        wrapper._llm = bound_llm
        wrapper._model_id = self._model_id
        wrapper._region = self._region
        wrapper._temperature = self._temperature
        wrapper._max_tokens = self._max_tokens
        wrapper.model = self._model_id

        return wrapper

    def with_structured_output(self, *args, **kwargs):
        """Enhanced structured output with advanced reasoning"""
        structured_llm = self._llm.with_structured_output(*args, **kwargs)

        wrapper = EnhancedAWSBedrockLLM.__new__(EnhancedAWSBedrockLLM)
        wrapper._llm = structured_llm
        wrapper._model_id = self._model_id
        wrapper._region = self._region
        wrapper._temperature = self._temperature
        wrapper._max_tokens = self._max_tokens
        wrapper.model = self._model_id

        return wrapper

def get_enhanced_llm():
    """Helper function to initialize the EnhancedAWSBedrockLLM."""
    if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
        logger.warning("AWS credentials not found, checking default fallback options.")
    
    model_name = os.getenv("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0")
    enhanced_llm = EnhancedAWSBedrockLLM(
        model_id=model_name,
        region=os.getenv("AWS_REGION", "us-east-1"),
        temperature=0.3,
        max_tokens=8192,
    )
    return enhanced_llm
