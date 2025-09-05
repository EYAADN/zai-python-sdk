"""Server-Sent Events parser."""

import json
from typing import Any, Dict, Optional


class SSEParser:
    """Parser for Server-Sent Events."""
    
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse Server-Sent Events line.
        
        Args:
            line (str): SSE line string.
        
        Returns:
            Optional[Dict[str, Any]]: Parsed data dictionary or None.
        """
        line = line.strip()
        
        if not line or line.startswith(":"):
            return None
        
        if line.startswith("data: "):
            data_str = line[6:]
            
            if data_str.strip():
                try:
                    return json.loads(data_str)
                except json.JSONDecodeError:
                    return None
        
        return None