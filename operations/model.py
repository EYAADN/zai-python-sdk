"""Model operations for Z.AI API."""

from typing import Dict, List, Optional

from ..core.http_client import HTTPClient
from ..models import Model


class ModelOperations:
    """Handles model-related operations."""
    
    def __init__(self, http_client: HTTPClient):
        """
        Initialize model operations.
        
        Args:
            http_client (HTTPClient): HTTP client instance.
        """
        self.http_client = http_client
    
    def get_models(self) -> List[Model]:
        """
        Get available models.
        
        Returns:
            List[Model]: List of available Model objects.
        """
        response = self.http_client.make_request("GET", "/api/v1/models")
        data = response.json()
        models = []
        
        for model_data in data.get("data", []):
            models.append(Model.from_dict(model_data))
        
        return models
    
    def get_model_by_id(self, model_id: str) -> Optional[Model]:
        """
        Get a specific model by ID.
        
        Args:
            model_id (str): The model ID to search for.
        
        Returns:
            Optional[Model]: Model object if found, None otherwise.
        """
        models = self.get_models()
        
        for model in models:
            if model.id == model_id:
                return model
        
        return None
    
    def build_model_item(
        self,
        model: str,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None
    ) -> Dict:
        """
        Build model_item configuration with custom parameters.
        
        Args:
            model (str): Model ID.
            temperature (float): Temperature value.
            top_p (float): Top-p value.
            max_tokens (int): Maximum tokens.
        
        Returns:
            Dict: Model item configuration dictionary.
        """
        model_configs = {
            "glm-4.5v": {
                "name": "GLM-4.5V",
                "temperature": 0.8,
                "top_p": 0.6,
                "max_tokens": 80000,
                "description": "Advanced visual understanding and analysis",
                "capabilities": {
                    "vision": True,
                    "citations": False,
                    "preview_mode": False,
                    "web_search": False,
                    "language_detection": False,
                    "restore_n_source": False,
                    "mcp": False,
                    "file_qa": False,
                    "returnFc": True,
                    "returnThink": True,
                    "think": True
                }
            },
            "0727-360B-API": {
                "name": "GLM-4.5",
                "temperature": 0.6,
                "top_p": 0.95,
                "max_tokens": 80000,
                "description": "Most advanced model, proficient in coding and tool use",
                "capabilities": {
                    "vision": False,
                    "citations": False,
                    "preview_mode": False,
                    "web_search": False,
                    "language_detection": False,
                    "restore_n_source": False,
                    "mcp": True,
                    "file_qa": True,
                    "returnFc": True,
                    "returnThink": True,
                    "think": True
                }
            }
        }
        
        config = model_configs.get(model, {
            "name": model.upper(),
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 4096,
            "description": "Custom model configuration",
            "capabilities": {
                "vision": False,
                "citations": False,
                "preview_mode": False,
                "web_search": False,
                "language_detection": False,
                "restore_n_source": False,
                "mcp": False,
                "file_qa": False,
                "returnFc": True,
                "returnThink": True,
                "think": True
            }
        })
        
        final_temperature = temperature if temperature is not None else config["temperature"]
        final_top_p = top_p if top_p is not None else config["top_p"]
        final_max_tokens = max_tokens if max_tokens is not None else config["max_tokens"]
        
        return {
            "id": model,
            "name": config["name"],
            "owned_by": "openai",
            "openai": {
                "id": model,
                "name": model,
                "owned_by": "openai",
                "openai": {
                    "id": model
                },
                "urlIdx": 1
            },
            "urlIdx": 1,
            "info": {
                "id": model,
                "user_id": "custom-user",
                "base_model_id": None,
                "name": config["name"],
                "params": {
                    "temperature": final_temperature,
                    "top_p": final_top_p,
                    "max_tokens": final_max_tokens
                },
                "meta": {
                    "profile_image_url": "/static/favicon.png",
                    "description": config["description"],
                    "capabilities": config["capabilities"]
                }
            }
        }