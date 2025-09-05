"""Z.AI Python SDK

A Python client for the Z.AI API.
"""

from .client import ZAIClient
from .core import ZAIError
from .models import (
    Chat,
    ChatCompletionResponse,
    ChatHistory,
    ChatResponse,
    MCPFeature,
    Message,
    Model,
    ModelCapabilities,
    ModelInfo,
    ModelMeta,
    ModelParams,
    StreamingChunk
)

__version__ = "1.0.0"
__author__ = "Z.AI SDK Team"

__all__ = [
    "ZAIClient",
    "ZAIError",
    "Model",
    "ModelCapabilities",
    "ModelParams",
    "ModelMeta",
    "ModelInfo",
    "Chat",
    "ChatHistory",
    "ChatResponse",
    "Message",
    "MCPFeature",
    "ChatCompletionResponse",
    "StreamingChunk"
]