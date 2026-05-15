"""
AWS Nova Pro LLM Plugin for LiveKit Agents
==========================================
Simplified implementation using AWS Bedrock Nova Pro for voice agents.
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any

import boto3
from livekit.agents import llm
from livekit.agents.llm import ChatContext, ChatMessage, ChatRole
from livekit.agents.llm._provider_format import aws as aws_format

from aws_config import bedrock_client, aws_region, bedrock_model, is_configured

logger = logging.getLogger(__name__)


class NovaProLLM(llm.LLM):
    """Simple AWS Nova Pro LLM implementation for LiveKit Agents."""

    def __init__(
        self,
        *,
        model_id: str = "amazon.nova-pro-v1:0",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = bedrock_client()

        logger.info(f"Nova Pro LLM initialized: {model_id}")

    def _format_messages(self, chat_ctx: ChatContext) -> tuple[list, list]:
        """Convert LiveKit messages to Nova format using official AWS formatter."""
        messages, format_data = aws_format.to_chat_ctx(chat_ctx)
        system_messages = format_data.system_messages or []
        return messages, system_messages

    def chat(self, *, chat_ctx: ChatContext, tools=None, tool_choice=None, conn_options=None, **kwargs) -> "llm.LLMStream":
        """Synchronous chat method (required by LLM base class)."""
        messages, system_messages = self._format_messages(chat_ctx)
        return NovaProLLMStream(
            llm=self,
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
            client=self._client,
            model_id=self.model_id,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=messages,
            system_messages=system_messages
        )

    async def agenerate(self, *, chat_ctx: ChatContext, tools=None, tool_choice=None, conn_options=None, **kwargs) -> "llm.LLMStream":
        """Generate response using Nova Pro."""
        messages, system_messages = self._format_messages(chat_ctx)
        return NovaProLLMStream(
            llm=self,
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
            client=self._client,
            model_id=self.model_id,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=messages,
            system_messages=system_messages
        )


class NovaProLLMStream(llm.LLMStream):
    """Simple stream implementation for Nova Pro."""

    def __init__(self, *, llm, chat_ctx, tools, conn_options, client, model_id: str, temperature: float, max_tokens: int, messages: list, system_messages: list = None):
        super().__init__(llm=llm, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._client = client
        self._model_id = model_id
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._messages = messages
        self._system_messages = system_messages or []

    async def _run(self) -> None:
        """Execute Nova Pro request."""
        try:
            # Prepare request for Nova Pro
            request = {
                "messages": self._messages,
                "inferenceConfig": {
                    "temperature": self._temperature,
                    "maxTokens": self._max_tokens,
                    "topP": 0.9
                }
            }

            # Add system messages if present (for Nova Pro)
            if self._system_messages:
                request["system"] = [{"text": msg} for msg in self._system_messages]

            # Make async call to Bedrock
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._invoke_model,
                request
            )

            # Process response
            await self._process_response(response)

        except Exception as e:
            logger.error(f"Nova Pro request failed: {e}")
            # Emit an error chunk
            chunk = llm.ChatChunk(
                id="error",
                delta=llm.ChoiceDelta(
                    content=f"I encountered an error: {str(e)}",
                    role="assistant"
                )
            )
            self._event_ch.send_nowait(chunk)

    def _invoke_model(self, request: dict) -> dict:
        """Synchronous Bedrock call."""
        response = self._client.invoke_model(
            modelId=self._model_id,
            body=json.dumps(request)
        )
        return json.loads(response['body'].read())

    async def _process_response(self, response: dict) -> None:
        """Process Nova response and emit chunks."""
        try:
            # Extract text from response
            if 'output' in response and 'message' in response['output']:
                message = response['output']['message']

                if 'content' in message and isinstance(message['content'], list):
                    for content_item in message['content']:
                        if 'text' in content_item:
                            text = content_item['text']

                            # Emit text in chunks for streaming effect
                            chunk_size = 20
                            for i in range(0, len(text), chunk_size):
                                chunk_text = text[i:i + chunk_size]

                                chunk = llm.ChatChunk(
                                    id=f"chunk-{i}",
                                    delta=llm.ChoiceDelta(
                                        content=chunk_text,
                                        role="assistant"
                                    )
                                )

                                self._event_ch.send_nowait(chunk)
                                await asyncio.sleep(0.02)  # Small delay for streaming

                # Final empty chunk to signal completion
                final_chunk = llm.ChatChunk(
                    id="final",
                    delta=llm.ChoiceDelta(
                        content="",
                        role="assistant"
                    )
                )
                self._event_ch.send_nowait(final_chunk)

        except Exception as e:
            logger.error(f"Failed to process Nova response: {e}")


def get_nova_pro_llm(temperature: float = 0.7, model_id: Optional[str] = None) -> NovaProLLM:
    """
    Create AWS Nova Pro LLM for LiveKit Agents.

    Args:
        temperature: Response creativity (0.0 = focused, 1.0 = creative)
        model_id: Nova model ID (defaults to amazon.nova-pro-v1:0)

    Returns:
        Configured Nova Pro LLM

    Required environment variables:
        - AWS_ACCESS_KEY_ID: AWS access key
        - AWS_SECRET_ACCESS_KEY: AWS secret key
        - AWS_REGION: AWS region (e.g., 'us-east-1')
        - AWS_BEDROCK_MODEL: Optional model override
    """
    if not is_configured():
        raise ValueError("AWS credentials not configured. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")

    model_id = model_id or bedrock_model()

    return NovaProLLM(
        model_id=model_id,
        temperature=temperature,
        max_tokens=2048
    )


def validate_nova_config() -> bool:
    """Validate AWS Nova Pro configuration."""
    if not is_configured():
        logger.error("AWS credentials not configured")
        return False

    try:
        # Test Bedrock client creation
        client = bedrock_client()
        logger.info("Nova Pro configuration validated")
        return True
    except Exception as e:
        logger.error(f"Nova Pro validation failed: {e}")
        return False


# Test script
if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    if validate_nova_config():
        print("✅ Nova Pro configuration is valid!")
        print(f"   Region: {aws_region()}")
        print(f"   Model: {bedrock_model()}")
        sys.exit(0)
    else:
        print("❌ Nova Pro configuration is incomplete!")
        sys.exit(1)