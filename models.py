"""Data models for Z.AI API responses and requests."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class ModelCapabilities:
    """Model capabilities configuration."""
    
    vision: bool = False
    citations: bool = False
    preview_mode: bool = False
    web_search: bool = False
    language_detection: bool = False
    restore_n_source: bool = False
    mcp: bool = False
    file_qa: bool = False
    returnFc: bool = False
    returnThink: bool = False
    think: bool = False


@dataclass
class ModelParams:
    """Model parameters configuration."""
    
    temperature: float = 0.6
    top_p: float = 0.95
    max_tokens: int = 80000
    top_k: Optional[int] = None


@dataclass
class ModelMeta:
    """Model metadata."""
    
    profile_image_url: str = "/static/favicon.png"
    description: str = ""
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    mcpServerIds: Optional[List[str]] = None
    suggestion_prompts: Optional[List[Dict[str, Any]]] = None
    tags: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ModelInfo:
    """Model information."""
    
    id: str
    user_id: str
    base_model_id: Optional[str]
    name: str
    params: ModelParams
    meta: ModelMeta
    access_control: Optional[Any] = None
    is_active: bool = True
    updated_at: int = 0
    created_at: int = 0


@dataclass
class Model:
    """Z.AI Model representation."""
    
    id: str
    name: str
    owned_by: str
    openai: Dict[str, Any]
    urlIdx: int
    info: ModelInfo
    actions: List[Any] = field(default_factory=list)
    tags: List[Dict[str, str]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Model":
        """
        Create Model from API response.
        
        Args:
            data (Dict[str, Any]): API response dictionary.
        
        Returns:
            Model: Instance of Model.
        """
        info_data = data["info"]
        
        capabilities_data = info_data["meta"].get("capabilities", {})
        capabilities = ModelCapabilities(**capabilities_data)
        
        params_data = info_data.get("params", {})
        params = ModelParams(**params_data)
        
        meta_data = info_data["meta"]
        meta = ModelMeta(
            profile_image_url=meta_data.get("profile_image_url", "/static/favicon.png"),
            description=meta_data.get("description", ""),
            capabilities=capabilities,
            mcpServerIds=meta_data.get("mcpServerIds"),
            suggestion_prompts=meta_data.get("suggestion_prompts"),
            tags=meta_data.get("tags", [])
        )
        
        info = ModelInfo(
            id=info_data["id"],
            user_id=info_data["user_id"],
            base_model_id=info_data.get("base_model_id"),
            name=info_data["name"],
            params=params,
            meta=meta,
            access_control=info_data.get("access_control"),
            is_active=info_data.get("is_active", True),
            updated_at=info_data.get("updated_at", 0),
            created_at=info_data.get("created_at", 0)
        )
        
        return cls(
            id=data["id"],
            name=data["name"],
            owned_by=data["owned_by"],
            openai=data["openai"],
            urlIdx=data["urlIdx"],
            info=info,
            actions=data.get("actions", []),
            tags=data.get("tags", [])
        )


@dataclass
class Message:
    """Chat message."""
    
    id: str
    parentId: Optional[str] = None
    childrenIds: List[str] = field(default_factory=list)
    role: str = "user"
    content: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time()))
    models: List[str] = field(default_factory=list)


@dataclass
class ChatHistory:
    """Chat history structure."""
    
    messages: Dict[str, Message] = field(default_factory=dict)
    currentId: Optional[str] = None


@dataclass
class MCPFeature:
    """MCP (Model Control Protocol) feature."""
    
    type: str
    server: str
    status: str


@dataclass
class Chat:
    """Z.AI Chat representation."""
    
    id: str = ""
    title: str = "New Chat"
    models: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    history: ChatHistory = field(default_factory=ChatHistory)
    messages: List[Message] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    features: List[MCPFeature] = field(default_factory=list)
    mcp_servers: List[str] = field(default_factory=list)
    enable_thinking: bool = True
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    
    def add_message(self, content: str, role: str = "user", models: List[str] = None) -> Message:
        """
        Add a message to the chat.
        
        Args:
            content (str): Message content.
            role (str): Role of the sender.
            models (List[str], optional): List of model IDs.
        
        Returns:
            Message: The created message instance.
        """
        message_id = str(uuid.uuid4())
        models = models or self.models
        
        message = Message(
            id=message_id,
            role=role,
            content=content,
            models=models
        )
        
        self.messages.append(message)
        self.history.messages[message_id] = message
        self.history.currentId = message_id
        
        return message


@dataclass
class ChatResponse:
    """Response from chat creation."""
    
    id: str
    user_id: str
    title: str
    chat: Chat
    updated_at: int
    created_at: int
    share_id: Optional[str] = None
    archived: bool = False
    pinned: bool = False
    meta: Dict[str, Any] = field(default_factory=dict)
    folder_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatResponse":
        """
        Create ChatResponse from API response.
        
        Args:
            data (Dict[str, Any]): API response dictionary.
        
        Returns:
            ChatResponse: Instance of ChatResponse.
        """
        chat_data = data["chat"]
        
        messages = []
        history_messages = {}
        
        for msg_data in chat_data.get("messages", []):
            message = Message(
                id=msg_data["id"],
                parentId=msg_data.get("parentId"),
                childrenIds=msg_data.get("childrenIds", []),
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=msg_data["timestamp"],
                models=msg_data.get("models", [])
            )
            messages.append(message)
            history_messages[message.id] = message
        
        features = []
        for feat_data in chat_data.get("features", []):
            features.append(MCPFeature(
                type=feat_data["type"],
                server=feat_data["server"],
                status=feat_data["status"]
            ))
        
        history = ChatHistory(
            messages=history_messages,
            currentId=chat_data.get("history", {}).get("currentId")
        )
        
        chat = Chat(
            id=chat_data.get("id", ""),
            title=chat_data.get("title", "New Chat"),
            models=chat_data.get("models", []),
            params=chat_data.get("params", {}),
            history=history,
            messages=messages,
            tags=chat_data.get("tags", []),
            flags=chat_data.get("flags", []),
            features=features,
            mcp_servers=chat_data.get("mcp_servers", []),
            enable_thinking=chat_data.get("enable_thinking", True),
            timestamp=chat_data.get("timestamp", int(time.time() * 1000))
        )
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            title=data["title"],
            chat=chat,
            updated_at=data["updated_at"],
            created_at=data["created_at"],
            share_id=data.get("share_id"),
            archived=data.get("archived", False),
            pinned=data.get("pinned", False),
            meta=data.get("meta", {}),
            folder_id=data.get("folder_id")
        )


@dataclass
class StreamingChunk:
    """Streaming response chunk."""
    
    type: str
    phase: str
    delta_content: str = ""
    done: bool = False
    usage: Optional[Dict[str, Any]] = None
    edit_index: Optional[int] = None
    edit_content: Optional[str] = None
    role: Optional[str] = None
    message_id: Optional[str] = None


@dataclass
class ChatCompletionResponse:
    """Complete chat completion response."""
    
    content: str
    thinking: str
    usage: Dict[str, Any]
    message_id: str
    done: bool = True