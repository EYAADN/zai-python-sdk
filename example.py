"""Example usage of Z.AI API Client."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from zai.client import ZAIClient
from zai.core.exceptions import ZAIError


def main():
    """
    Main function demonstrating Z.AI client usage.
    
    Returns:
        None: Executes example chat interactions.
    """
    try:
        print("Initializing Z.AI Client...")
        client = ZAIClient(auto_auth=True, verbose=False)
        print(f"Got token: {client.token[:20]}...")
        
        print("\n" + "="*50)
        print("Simple Chat Example")
        print("="*50)
        
        try:
            response = client.simple_chat(
                message="What is the capital of France?",
                model="glm-4.5v",
                enable_thinking=False,
                temperature=0.7,
                top_p=0.9,
                max_tokens=500
            )
            
            if response.content:
                print(f"\nResponse: {response.content}")
            else:
                print("\nNo content in response")
            
            if response.thinking:
                print(f"\nThinking: {response.thinking}")
            
            if response.usage:
                print(f"\nUsage: {response.usage}")
        except Exception as chat_error:
            print(f"Chat error: {chat_error}")
        
        
        print("\n" + "="*50)
        print("Testing with Code Model")
        print("="*50)
        
        try:
            response2 = client.simple_chat(
                message="Say 'Hello World'",
                model="0727-360B-API",
                enable_thinking=False,
                temperature=0.5,
                max_tokens=100
            )
            
            if response2.content:
                print(f"\nResponse: {response2.content}")
            else:
                print("\nNo content in second response")
                
        except Exception as chat2_error:
            print(f"Second chat error: {chat2_error}")
        
    except ZAIError as e:
        print(f"ZAI Error: {e}")
    except Exception as e:
        import traceback
        print(f"Unexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    main()