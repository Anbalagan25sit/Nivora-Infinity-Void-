"""
Azure OpenAI LLM Plugin for LiveKit Agents
==========================================
Uses Azure OpenAI GPT-4o for the voice agent LLM.

This wraps the OpenAI plugin to work with Azure endpoints.
"""

import os
import logging
from typing import Optional
from livekit.plugins import openai

logger = logging.getLogger(__name__)


def get_azure_llm(
    deployment: Optional[str] = None,
    temperature: float = 0.7,
) -> openai.LLM:
    """
    Create an Azure OpenAI LLM instance for LiveKit Agents.

    Args:
        deployment: Azure deployment name (defaults to AZURE_OPENAI_DEPLOYMENT env var)
        temperature: Response creativity (0.0 = focused, 1.0 = creative)

    Returns:
        Configured OpenAI LLM that uses Azure backend

    Required environment variables:
        - AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL
        - AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
        - AZURE_OPENAI_DEPLOYMENT: Model deployment name (e.g., 'gpt-4o')
        - AZURE_OPENAI_API_VERSION: API version (e.g., '2024-08-01-preview')
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o").strip()
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview").strip()

    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT not set in environment")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY not set in environment")

    # Remove trailing slash from endpoint
    endpoint = endpoint.rstrip("/")

    logger.info(f"Initializing Azure OpenAI LLM:")
    logger.info(f"  Endpoint: {endpoint}")
    logger.info(f"  Deployment: {deployment}")
    logger.info(f"  API Version: {api_version}")
    logger.info(f"  Temperature: {temperature}")

    # Create OpenAI LLM with Azure configuration
    # LiveKit's OpenAI plugin supports Azure via base_url and azure parameters
    llm = openai.LLM.with_azure(
        deployment=deployment,
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        temperature=temperature,
    )

    logger.info("Azure OpenAI LLM initialized successfully!")
    return llm


def validate_azure_config() -> bool:
    """
    Validate that all required Azure OpenAI environment variables are set.

    Returns:
        True if all required variables are set, False otherwise
    """
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var, "").strip()
        if not value:
            missing.append(var)

    if missing:
        logger.error(f"Missing Azure OpenAI config: {', '.join(missing)}")
        return False

    logger.info("Azure OpenAI configuration validated successfully")
    return True


# Quick test
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    logging.basicConfig(level=logging.INFO)

    if validate_azure_config():
        print("\n✅ Azure OpenAI configuration is valid!")
        print(f"   Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"   Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
    else:
        print("\n❌ Azure OpenAI configuration is incomplete!")
