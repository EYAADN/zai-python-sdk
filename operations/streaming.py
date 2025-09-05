"""Streaming operations for Z.AI API."""

import json
import time
from typing import Any, Dict, Generator, List, Optional

from ..core.http_client import HTTPClient
from ..models import StreamingChunk
from ..utils.sse_parser import SSEParser


class StreamingOperations:
    """Handles streaming operations."""
    
    def __init__(self, http_client: HTTPClient):
        """
        Initialize streaming operations.
        
        Args:
            http_client (HTTPClient): HTTP client instance.
        """
        self.http_client = http_client
        self.sse_parser = SSEParser()
    
    def stream_completion(
        self,
        chat_id: str,
        messages: List[Dict[str, str]],
        model: str = "0727-360B-API",
        enable_thinking: bool = True,
        features: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, str]] = None,
        model_ops: Optional[Any] = None
    ) -> Generator[StreamingChunk, None, None]:
        """
        Stream chat completion.
        
        Args:
            chat_id (str): Chat ID.
            messages (List[Dict[str, str]]): List of messages in OpenAI format.
            model (str): Model ID to use.
            enable_thinking (bool): Enable thinking phase.
            features (Optional[Dict[str, Any]]): Features configuration.
            variables (Optional[Dict[str, str]]): Template variables.
            model_ops (Optional[Any]): Model operations instance.
        
        Yields:
            StreamingChunk: StreamingChunk objects.
        """
        if features is None:
            features = self._get_default_features(enable_thinking)
        
        if variables is None:
            variables = self._get_default_variables()
        
        model_item = self._get_model_item(model, model_ops)
        
        payload = {
            "stream": True,
            "model": model,
            "messages": messages,
            "params": {},
            "features": features,
            "variables": variables,
            "model_item": model_item,
            "chat_id": chat_id
        }
        
        response = self.http_client.make_request(
            "POST",
            "/api/chat/completions",
            payload,
            stream=True
        )
        
        for line in response.iter_lines(decode_unicode=True):
            if line:
                data = self.sse_parser.parse_line(line)
                if data:
                    chunk = self._create_streaming_chunk(data)
                    yield chunk
                    if chunk.done:
                        break
    
    def _get_default_features(self, enable_thinking: bool) -> Dict[str, Any]:
        """
        Get default features configuration.
        
        Args:
            enable_thinking (bool): Enable thinking mode.
        
        Returns:
            Dict[str, Any]: Default features configuration.
        """
        return {
            "image_generation": False,
            "web_search": False,
            "auto_web_search": False,
            "preview_mode": True,
            "flags": [],
            "features": [
                {"type": "mcp", "server": "vibe-coding", "status": "hidden"},
                {"type": "mcp", "server": "ppt-maker", "status": "hidden"},
                {"type": "mcp", "server": "image-search", "status": "hidden"}
            ],
            "enable_thinking": enable_thinking
        }
    
    def _get_default_variables(self) -> Dict[str, str]:
        """
        Get default template variables.
        
        Returns:
            Dict[str, str]: Default template variables.
        """
        return {
            "{{USER_NAME}}": "Guest",
            "{{USER_LOCATION}}": "Unknown",
            "{{CURRENT_DATETIME}}": time.strftime("%Y-%m-%d %H:%M:%S"),
            "{{CURRENT_DATE}}": time.strftime("%Y-%m-%d"),
            "{{CURRENT_TIME}}": time.strftime("%H:%M:%S"),
            "{{CURRENT_WEEKDAY}}": time.strftime("%A"),
            "{{CURRENT_TIMEZONE}}": "UTC",
            "{{USER_LANGUAGE}}": "en-US"
        }
    
    def _get_model_item(self, model: str, model_ops: Optional[Any]) -> Dict:
        """
        Get model item configuration.
        
        Args:
            model (str): Model ID.
            model_ops (Optional[Any]): Model operations instance.
        
        Returns:
            Dict: Model item configuration.
        """
        if model_ops:
            model_obj = model_ops.get_model_by_id(model)
            model_item = {
                "id": model,
                "name": model_obj.name if model_obj else model
            }
            
            if model_obj:
                model_item.update({
                    "owned_by": model_obj.owned_by,
                    "openai": model_obj.openai,
                    "urlIdx": model_obj.urlIdx,
                    "info": {
                        "id": model_obj.info.id,
                        "name": model_obj.info.name,
                        "params": {
                            "temperature": model_obj.info.params.temperature,
                            "top_p": model_obj.info.params.top_p,
                            "max_tokens": model_obj.info.params.max_tokens
                        }
                    }
                })
            
            return model_item
        
        return {"id": model, "name": model}
    
    def _create_streaming_chunk(self, data: Dict[str, Any]) -> StreamingChunk:
        """
        Create StreamingChunk from parsed data.
        
        Args:
            data (Dict[str, Any]): Parsed SSE data.
        
        Returns:
            StreamingChunk: Created streaming chunk.
        """
        chunk_data = data.get("data", {})
        
        return StreamingChunk(
            type=data.get("type", ""),
            phase=chunk_data.get("phase", ""),
            delta_content=chunk_data.get("delta_content", ""),
            done=chunk_data.get("done", False),
            usage=chunk_data.get("usage"),
            edit_index=chunk_data.get("edit_index"),
            edit_content=chunk_data.get("edit_content"),
            role=chunk_data.get("role"),
            message_id=chunk_data.get("message_id")
        )