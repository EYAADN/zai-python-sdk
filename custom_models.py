"""Custom model presets for Z.AI API with different parameters."""

CREATIVE_WRITER = {
    "model": "glm-4.5v",
    "temperature": 1.2,
    "top_p": 0.9,
    "max_tokens": 4000,
    "description": "Creative writing with high randomness"
}

CODE_ASSISTANT = {
    "model": "0727-360B-API",
    "temperature": 0.2,
    "top_p": 0.7,
    "max_tokens": 8000,
    "description": "Precise code generation and debugging"
}

BALANCED_CHAT = {
    "model": "glm-4.5v",
    "temperature": 0.7,
    "top_p": 0.8,
    "max_tokens": 2000,
    "description": "Balanced conversational responses"
}

RESEARCH_ASSISTANT = {
    "model": "0727-360B-API",
    "temperature": 0.4,
    "top_p": 0.85,
    "max_tokens": 6000,
    "description": "Thorough research and analysis"
}

BRAINSTORMER = {
    "model": "glm-4.5v",
    "temperature": 1.5,
    "top_p": 0.95,
    "max_tokens": 3000,
    "description": "Creative brainstorming and ideation"
}

CONSERVATIVE = {
    "model": "0727-360B-API",
    "temperature": 0.1,
    "top_p": 0.5,
    "max_tokens": 1500,
    "description": "Conservative, factual responses"
}

CUSTOM_PRESETS = {
    "creative": CREATIVE_WRITER,
    "code": CODE_ASSISTANT,
    "balanced": BALANCED_CHAT,
    "research": RESEARCH_ASSISTANT,
    "brainstorm": BRAINSTORMER,
    "conservative": CONSERVATIVE
}


def get_preset(name: str) -> dict:
    """
    Get a custom preset by name.
    
    Args:
        name (str): The name of the preset to retrieve.
    
    Returns:
        dict: The preset dictionary corresponding to the given name.
              If the name is not found, returns the BALANCED_CHAT preset.
    """
    return CUSTOM_PRESETS.get(name.lower(), BALANCED_CHAT)


def list_presets() -> list:
    """
    List all available preset names.
    
    Returns:
        list: A list of all available preset names as strings.
    """
    return list(CUSTOM_PRESETS.keys())