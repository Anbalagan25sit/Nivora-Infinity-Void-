"""
AWS Configuration — Centralized boto3 client factory.

Required environment variables (set in .env):
    AWS_ACCESS_KEY_ID        – IAM access key
    AWS_SECRET_ACCESS_KEY    – IAM secret key
    AWS_REGION               – e.g. us-east-1
    AWS_S3_BUCKET            – S3 bucket for screenshots / files
    AWS_DYNAMODB_TABLE       – DynamoDB table name for habits (default: nivora_habits)
    AWS_SES_SENDER_EMAIL     – Verified SES sender email address

Optional:
    AWS_BEDROCK_MODEL        – Bedrock model ID (default: meta.llama3-3-70b-instruct-v1:0)
    AWS_POLLY_VOICE          – Polly voice ID (default: Matthew)
"""

import os
import logging
from functools import lru_cache

import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


def aws_region() -> str:
    return _env("AWS_REGION", "us-east-1")


def s3_bucket() -> str:
    return _env("AWS_S3_BUCKET", "nivora-bucket")


def dynamodb_table() -> str:
    return _env("AWS_DYNAMODB_TABLE", "nivora_habits")


def ses_sender() -> str:
    return _env("AWS_SES_SENDER_EMAIL", "")


def bedrock_model() -> str:
    return _env("AWS_BEDROCK_MODEL", "amazon.nova-pro-v1:0")


def polly_voice() -> str:
    return _env("AWS_POLLY_VOICE", "Matthew")


# ---------------------------------------------------------------------------
# Boto3 session & clients  (cached so we don't create new ones every call)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_session() -> boto3.Session:
    """Create a reusable boto3 session from env vars."""
    return boto3.Session(
        aws_access_key_id=_env("AWS_ACCESS_KEY_ID") or None,
        aws_secret_access_key=_env("AWS_SECRET_ACCESS_KEY") or None,
        region_name=aws_region(),
    )


def _client(service: str):
    """Get a boto3 client for the given AWS service."""
    return get_session().client(
        service,
        config=Config(retries={"max_attempts": 2, "mode": "standard"}),
    )


@lru_cache(maxsize=1)
def ses_client():
    return _client("ses")


@lru_cache(maxsize=1)
def s3_client():
    return _client("s3")


@lru_cache(maxsize=1)
def dynamodb_resource():
    return get_session().resource("dynamodb", region_name=aws_region())


@lru_cache(maxsize=1)
def dynamodb_table_resource():
    return dynamodb_resource().Table(dynamodb_table())


@lru_cache(maxsize=1)
def bedrock_client():
    return _client("bedrock-runtime")


# ---------------------------------------------------------------------------
# Quick health check
# ---------------------------------------------------------------------------

def is_configured() -> bool:
    """Return True if the minimum AWS credentials are present."""
    return bool(_env("AWS_ACCESS_KEY_ID") and _env("AWS_SECRET_ACCESS_KEY"))

def bedrock_guardrail() -> dict:
    """Define and return the Bedrock guardrail configuration."""
    return {
        "sexual_content": "NONE",  # Disable filtering for sexual content
        "hate_speech": "MEDIUM",  # Medium filtering for hate speech
        "insults": "MEDIUM",      # Medium filtering for insults
        "violence": "MEDIUM"      # Medium filtering for violence
    }
