"""Chat operations for Z.AI API."""

import time
import uuid
from typing import Dict, List, Optional

from ..core.exceptions import ZAIError
from ..core.http_client import HTTPClient
from ..models import Chat, ChatCompletionResponse, ChatResponse, MCPFeature
from .model import ModelOperations
from .streaming import StreamingOperations


class ChatOperations:
    """Handles chat-related operations."""
    
    def __init__(
        self,
        http_client: HTTPClient,
        model_ops: ModelOperations,
        auth_data: Optional[Dict] = None
    ):
        """
        Initialize chat operations.
        
        Args:
            http_client (HTTPClient): HTTP client instance.
            model_ops (ModelOperations): Model operations instance.
            auth_data (Optional[Dict]): Authentication data.
        """
        self.http_client = http_client
        self.model_ops = model_ops
        self.auth_data = auth_data
        self.verbose = http_client.verbose
        self.streaming_ops = StreamingOperations(http_client)
    
    def create_chat(
        self,
        title: str = "New Chat",
        models: List[str] = None,
        initial_message: Optional[str] = None,
        enable_thinking: bool = True,
        features: List[MCPFeature] = None
    ) -> ChatResponse:
        """
        Create a new chat.
        
        Args:
            title (str): Chat title.
            models (List[str]): List of model IDs to use.
            initial_message (Optional[str]): Optional initial message.
            enable_thinking (bool): Enable thinking mode.
            features (List[MCPFeature]): MCP features configuration.
        
        Returns:
            ChatResponse: ChatResponse object.
        """
        models = models or ["0727-360B-API"]
        features = features or [
            MCPFeature("mcp", "vibe-coding", "hidden"),
            MCPFeature("mcp", "ppt-maker", "hidden"),
            MCPFeature("mcp", "image-search", "hidden")
        ]
        
        chat = Chat(
            title=title,
            models=models,
            enable_thinking=enable_thinking,
            features=features
        )
        
        if initial_message:
            chat.add_message(initial_message, "user", models)
        
        payload = self._build_chat_payload(chat)
        response = self.http_client.make_request("POST", "/api/v1/chats/new", payload)
        
        return ChatResponse.from_dict(response.json())
    
    def _build_chat_payload(self, chat: Chat) -> Dict:
        """
        Build chat creation payload.
        
        Args:
            chat (Chat): Chat object.
        
        Returns:
            Dict: Chat creation payload.
        """
        return {
            "chat": {
                "id": chat.id,
                "title": chat.title,
                "models": chat.models,
                "params": chat.params,
                "history": {
                    "messages": {
                        msg.id: {
                            "id": msg.id,
                            "parentId": msg.parentId,
                            "childrenIds": msg.childrenIds,
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp,
                            "models": msg.models
                        } for msg in chat.messages
                    },
                    "currentId": chat.history.currentId
                },
                "messages": [
                    {
                        "id": msg.id,
                        "parentId": msg.parentId,
                        "childrenIds": msg.childrenIds,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "models": msg.models
                    } for msg in chat.messages
                ],
                "tags": chat.tags,
                "flags": chat.flags,
                "features": [
                    {
                        "type": feat.type,
                        "server": feat.server,
                        "status": feat.status
                    } for feat in chat.features
                ],
                "mcp_servers": chat.mcp_servers,
                "enable_thinking": chat.enable_thinking,
                "timestamp": chat.timestamp
            }
        }
    
    def complete_chat(
        self,
        chat_id: str,
        messages: List[Dict[str, str]],
        model: str = "0727-360B-API",
        enable_thinking: bool = True
    ) -> ChatCompletionResponse:
        """
        Complete chat and return full response.
        
        Args:
            chat_id (str): Chat ID.
            messages (List[Dict[str, str]]): List of messages.
            model (str): Model ID.
            enable_thinking (bool): Enable thinking mode.
        
        Returns:
            ChatCompletionResponse: ChatCompletionResponse with complete content.
        """
        content = ""
        thinking = ""
        usage = None
        message_id = None
        current_phase = None
        
        for chunk in self.streaming_ops.stream_completion(
            chat_id=chat_id,
            messages=messages,
            model=model,
            enable_thinking=enable_thinking,
            model_ops=self.model_ops
        ):
            if chunk.phase == "thinking":
                thinking += chunk.delta_content
                current_phase = "thinking"
            elif chunk.phase == "answer":
                content += chunk.delta_content
                current_phase = "answer"
            elif chunk.phase == "other" and chunk.edit_content:
                if current_phase == "thinking":
                    thinking = chunk.edit_content
                elif current_phase == "answer":
                    content += chunk.edit_content
            
            if chunk.usage:
                usage = chunk.usage
            if chunk.message_id:
                message_id = chunk.message_id
        
        return ChatCompletionResponse(
            content=content.strip(),
            thinking=thinking.strip(),
            usage=usage or {},
            message_id=message_id or "",
            done=True
        )
    
    def simple_chat(
        self,
        message: str,
        model: str = "glm-4.5v",
        enable_thinking: bool = True,
        chat_title: str = "Simple Chat",
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None
    ) -> ChatCompletionResponse:
        """
        Simple one-shot chat completion using the actual Z.AI API.
        
        Args:
            message (str): User message.
            model (str): Model ID (e.g., 'glm-4.5v', '0727-360B-API').
            enable_thinking (bool): Enable thinking mode.
            chat_title (str): Chat title.
            temperature (float): Controls randomness (0.0-2.0, default varies by model).
            top_p (float): Controls diversity (0.0-1.0, default varies by model).
            max_tokens (int): Maximum response length (default varies by model).
        
        Returns:
            ChatCompletionResponse: ChatCompletionResponse with AI response.
        """
        chat_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        chat_payload = self._build_simple_chat_payload(
            chat_id, message_id, message, model, chat_title, 
            enable_thinking, timestamp
        )
        
        self.http_client.update_headers({"x-fe-version": "prod-fe-1.0.70"})
        
        try:
            response = self.http_client.make_request("POST", "/api/v1/chats/new", chat_payload)
            chat_data = response.json()
            actual_chat_id = chat_data.get("id")
            
            if not actual_chat_id:
                raise ZAIError("Failed to create chat - no chat ID returned")
            
            current_message_id = None
            if "chat" in chat_data and "history" in chat_data["chat"]:
                current_message_id = chat_data["chat"]["history"].get("currentId")
            
            if not current_message_id:
                current_message_id = message_id
            
            return self._complete_simple_chat(
                actual_chat_id, message, model, enable_thinking,
                temperature, top_p, max_tokens
            )
            
        except Exception as e:
            raise ZAIError(f"Simple chat failed: {e}")
    
    def _build_simple_chat_payload(
        self,
        chat_id: str,
        message_id: str,
        message: str,
        model: str,
        chat_title: str,
        enable_thinking: bool,
        timestamp: int
    ) -> Dict:
        """
        Build simple chat creation payload.
        
        Args:
            chat_id (str): Chat ID.
            message_id (str): Message ID.
            message (str): User message.
            model (str): Model ID.
            chat_title (str): Chat title.
            enable_thinking (bool): Enable thinking mode.
            timestamp (int): Timestamp.
        
        Returns:
            Dict: Simple chat creation payload.
        """
        return {
            "chat": {
                "id": "",
                "title": chat_title,
                "models": [model],
                "params": {},
                "history": {
                    "messages": {
                        message_id: {
                            "id": message_id,
                            "parentId": None,
                            "childrenIds": [],
                            "role": "user",
                            "content": message,
                            "timestamp": timestamp,
                            "models": [model]
                        }
                    },
                    "currentId": message_id
                },
                "messages": [{
                    "id": message_id,
                    "parentId": None,
                    "childrenIds": [],
                    "role": "user",
                    "content": message,
                    "timestamp": timestamp,
                    "models": [model]
                }],
                "tags": [],
                "flags": [],
                "mcp_servers": [],
                "enable_thinking": enable_thinking,
                "timestamp": timestamp * 1000
            }
        }
    
    def _complete_simple_chat(
        self,
        chat_id: str,
        message: str,
        model: str,
        enable_thinking: bool,
        temperature: float,
        top_p: float,
        max_tokens: int
    ) -> ChatCompletionResponse:
        """
        Complete simple chat streaming.
        
        Args:
            chat_id (str): Actual chat ID.
            message (str): User message.
            model (str): Model ID.
            enable_thinking (bool): Enable thinking mode.
            temperature (float): Temperature parameter.
            top_p (float): Top-p parameter.
            max_tokens (int): Max tokens parameter.
        
        Returns:
            ChatCompletionResponse: Completed chat response.
        """
        completion_payload = {
            "stream": True,
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "params": {},
            "features": {
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
            },
            "variables": self._get_variables(),
            "model_item": self.model_ops.build_model_item(model, temperature, top_p, max_tokens),
            "chat_id": chat_id,
            "id": str(uuid.uuid4())
        }
        
        original_referer = self.http_client.session.headers.get("referer")
        self.http_client.session.headers["referer"] = f"https://chat.z.ai/c/{chat_id}"
        
        try:
            return self._parse_stream_response(
                self.http_client.make_request("POST", "/api/chat/completions", completion_payload, stream=True)
            )
        finally:
            if original_referer:
                self.http_client.session.headers["referer"] = original_referer
    
    def _get_variables(self) -> Dict[str, str]:
        """
        Get template variables.
        
        Returns:
            Dict[str, str]: Template variables dictionary.
        """
        return {
            "{{USER_NAME}}": self.auth_data.get('name', 'Guest') if self.auth_data else 'Guest',
            "{{USER_LOCATION}}": "Unknown",
            "{{CURRENT_DATETIME}}": time.strftime("%Y-%m-%d %H:%M:%S"),
            "{{CURRENT_DATE}}": time.strftime("%Y-%m-%d"),
            "{{CURRENT_TIME}}": time.strftime("%H:%M:%S"),
            "{{CURRENT_WEEKDAY}}": time.strftime("%A"),
            "{{CURRENT_TIMEZONE}}": "America/New_York",
            "{{USER_LANGUAGE}}": "en-US"
        }
    
    def _parse_stream_response(self, stream_response) -> ChatCompletionResponse:
        """
        Parse streaming response.
        
        Args:
            stream_response: Streaming response object.
        
        Returns:
            ChatCompletionResponse: Parsed completion response.
        """
        import json
        
        content = ""
        thinking = ""
        usage = {}
        
        try:
            line_count = 0
            for line in stream_response.iter_lines(decode_unicode=True, chunk_size=8192):
                line_count += 1
                if self.verbose and line_count <= 5:
                    print(f"[DEBUG] Line {line_count}: {line[:200]}")
                
                if line and line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip():
                        try:
                            data = json.loads(data_str)
                            chunk_data = data.get("data", {})
                            phase = chunk_data.get("phase", "")
                            delta_content = chunk_data.get("delta_content", "")
                            done = chunk_data.get("done", False)
                            
                            if delta_content:
                                if phase == "thinking":
                                    thinking += delta_content
                                elif phase == "answer":
                                    content += delta_content
                            
                            if phase == "done" or done:
                                usage = chunk_data.get("usage", {})
                                break
                            
                            if chunk_data.get("usage"):
                                usage = chunk_data.get("usage", {})
                                
                        except json.JSONDecodeError as json_error:
                            if self.verbose:
                                print(f"[DEBUG] JSON decode error: {json_error}")
                                print(f"[DEBUG] Failed to parse: {data_str[:200]}")
                            continue
                            
        except Exception as stream_error:
            if not content and not thinking:
                raise ZAIError(f"Stream parsing failed: {stream_error}")
            if self.verbose:
                print(f"Stream parsing warning: {stream_error}, continuing with partial content")
        
        return ChatCompletionResponse(
            content=content.strip(),
            thinking=thinking.strip(),
            usage=usage,
            message_id="",
            done=True
        )