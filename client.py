"""Z.AI API Client."""

from typing import Dict, Generator, List, Optional

from .core import AuthManager, HTTPClient, ZAIError
from .models import ChatCompletionResponse, ChatResponse, MCPFeature, Model, StreamingChunk
from .operations import ChatOperations, ModelOperations


class ZAIClient:
    """Z.AI API Client."""
    
    def __init__(
        self,
        token: str = None,
        base_url: str = "https://chat.z.ai",
        timeout: int = 180,
        auto_auth: bool = True,
        verbose: bool = False
    ):
        """
        Initialize Z.AI client.
        
        Args:
            token (str): Bearer token for authentication (optional if auto_auth=True).
            base_url (str): Base URL for Z.AI API.
            timeout (int): Request timeout in seconds.
            auto_auth (bool): Automatically get guest token if no token provided.
            verbose (bool): Enable verbose output for debugging.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.verbose = verbose
        
        self.http_client = HTTPClient(base_url, timeout, verbose=verbose)
        self.auth_manager = AuthManager(self.http_client)
        self.model_ops = ModelOperations(self.http_client)
        
        if not token and auto_auth:
            token = self.auth_manager.get_guest_token()
        
        if token:
            self.auth_manager.set_token(token)
        
        self.chat_ops = ChatOperations(
            self.http_client,
            self.model_ops,
            self.auth_manager.get_auth_data()
        )
    
    @property
    def token(self) -> Optional[str]:
        """
        Get current authentication token.
        
        Returns:
            Optional[str]: Current token if set.
        """
        return self.auth_manager.token
    
    @property
    def auth_data(self) -> Optional[Dict]:
        """
        Get authentication data.
        
        Returns:
            Optional[Dict]: Authentication data if available.
        """
        return self.auth_manager.get_auth_data()
    
    @property
    def session(self):
        """
        Get HTTP session.
        
        Returns:
            requests.Session: Current session object.
        """
        return self.http_client.session
    
    def get_models(self) -> List[Model]:
        """
        Get available models.
        
        Returns:
            List[Model]: List of available Model objects.
        """
        return self.model_ops.get_models()
    
    def get_model_by_id(self, model_id: str) -> Optional[Model]:
        """
        Get a specific model by ID.
        
        Args:
            model_id (str): The model ID to search for.
        
        Returns:
            Optional[Model]: Model object if found, None otherwise.
        """
        return self.model_ops.get_model_by_id(model_id)
    
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
        return self.chat_ops.create_chat(
            title=title,
            models=models,
            initial_message=initial_message,
            enable_thinking=enable_thinking,
            features=features
        )
    
    def stream_completion(
        self,
        chat_id: str,
        messages: List[Dict[str, str]],
        model: str = "0727-360B-API",
        enable_thinking: bool = True,
        features: Optional[Dict] = None,
        variables: Optional[Dict[str, str]] = None
    ) -> Generator[StreamingChunk, None, None]:
        """
        Stream chat completion.
        
        Args:
            chat_id (str): Chat ID.
            messages (List[Dict[str, str]]): List of messages in OpenAI format.
            model (str): Model ID to use.
            enable_thinking (bool): Enable thinking phase.
            features (Optional[Dict]): Features configuration.
            variables (Optional[Dict[str, str]]): Template variables.
        
        Yields:
            StreamingChunk: StreamingChunk objects.
        """
        return self.chat_ops.streaming_ops.stream_completion(
            chat_id=chat_id,
            messages=messages,
            model=model,
            enable_thinking=enable_thinking,
            features=features,
            variables=variables,
            model_ops=self.model_ops
        )
    
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
        return self.chat_ops.complete_chat(
            chat_id=chat_id,
            messages=messages,
            model=model,
            enable_thinking=enable_thinking
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
        return self.chat_ops.simple_chat(
            message=message,
            model=model,
            enable_thinking=enable_thinking,
            chat_title=chat_title,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )