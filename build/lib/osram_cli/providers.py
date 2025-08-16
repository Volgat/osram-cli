import os
import json
from typing import Dict, Any, Generator
import requests
from rich.console import Console

console = Console()

# List of available models per provider
AVAILABLE_MODELS = {
    "zai": [
        "GLM-4.5",
        "GLM-4-Plus",
        "GLM-4.5-X",
        "GLM-4.5-Air",
        "GLM-4.5-AirX",
        "GLM-4.5-Flash",
        "GLM-4-32B-0414-128K",
        "ViduQ1-text",
        "viduq1-image",
        "viduq1-start-end",
        "vidu2-image",
        "vidu2-start-end",
        "vidu2-reference",
        "CogVideoX-3",
        "GLM-4.5V",
        "Vidu 2"
    ],
    "claude": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-sonnet-4-20250514",
        "claude-opus-4-1-20250805",
        "claude-opus-4-20250214",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
    ],
    "gemini": [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-1.0-pro-latest",
        "gemini-2.5-flash",
        "gemini-2.5-pro"
    ],
    "openai": [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-o3-2025-04-16",
        "gpt-5-2025-08-07"
    ],
    "qwen": [
        "Qwen3-Coder",
        "Qwen3-235B-A22B",
        "Qwen3-30B-A3B",
        "Qwen2.5-Max",
        "Qwen3-Coder-Flash",
        "Qwen2.5-Plus",
        "Qwen2.5-Turbo",
        "QVQ-Max",
        "Qwen2.5-Omni-7B",
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen-max-longcontext"
    ]
}

class BaseProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.endpoint = config["endpoint"]
    
    def prepare_headers(self) -> Dict[str, str]:
        raise NotImplementedError
    
    def prepare_body(self, messages: list) -> Dict[str, Any]:
        raise NotImplementedError
    
    def parse_stream(self, response: requests.Response) -> Generator[str, None, None]:
        raise NotImplementedError

class ZhipuProvider(BaseProvider):
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_body(self, messages: list) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
    
    def parse_stream(self, response: requests.Response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    data_str = decoded[6:]
                    # Skip empty data or [DONE] markers
                    if not data_str or data_str.strip() == "[DONE]":
                        continue
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and data["choices"]:
                            content = data["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue

class AnthropicProvider(BaseProvider):
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    def prepare_body(self, messages: list) -> Dict[str, Any]:
        return {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": msg["role"], "content": msg["content"]} for msg in messages],
            "stream": True
        }
    
    def parse_stream(self, response: requests.Response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    try:
                        data = json.loads(decoded[6:])
                        if data.get("type") == "content_block_delta":
                            content = data.get("delta", {}).get("text", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue

class GoogleProvider(BaseProvider):
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json"
        }
    
    def prepare_body(self, messages: list) -> Dict[str, Any]:
        formatted_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            formatted_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        return {
            "contents": formatted_messages,
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }
    
    def parse_stream(self, response: requests.Response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                try:
                    data = json.loads(decoded)
                    if "candidates" in data and data["candidates"]:
                        content = data["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue

class OpenAIProvider(BaseProvider):
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_body(self, messages: list) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
    
    def parse_stream(self, response: requests.Response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith("data: "):
                    data_str = decoded[6:]
                    # Skip empty data or [DONE] markers
                    if not data_str or data_str.strip() == "[DONE]":
                        continue
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and data["choices"]:
                            content = data["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue

class QwenProvider(BaseProvider):
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_body(self, messages: list) -> Dict[str, Any]:
        return {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "stream": True
            }
        }
    
    def parse_stream(self, response: requests.Response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                try:
                    data = json.loads(decoded)
                    if "output" in data and "choices" in data["output"]:
                        content = data["output"]["choices"][0].get("message", {}).get("content", "")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue

PROVIDERS = {
    "zai": ZhipuProvider,
    "claude": AnthropicProvider,
    "gemini": GoogleProvider,
    "openai": OpenAIProvider,
    "qwen": QwenProvider
}

def call_api(messages, provider_name=None, model_name=None, temperature=None, max_tokens=None):
    """Call AI API with the specified provider"""
    from .utils import load_config
    
    config = load_config()
    
    # Use specified provider or current provider
    provider_name = provider_name or config.get("current_provider", "zai")
    
    if provider_name not in config["providers"]:
        console.print(f"[red]Provider '{provider_name}' not configured[/red]")
        return None
    
    provider_config = config["providers"][provider_name].copy()
    
    # Override model if specified
    if model_name:
        provider_config["model"] = model_name
    
    # Get provider class
    provider_class = PROVIDERS.get(provider_name)
    if not provider_class:
        console.print(f"[red]Provider '{provider_name}' not implemented[/red]")
        return None
    
    # Create provider instance
    provider = provider_class(provider_config)
    
    # Format endpoint with variables if needed
    endpoint = provider.endpoint.format(
        model=provider.model,
        api_key=provider.api_key
    )
    
    try:
        response = requests.post(
            endpoint,
            headers=provider.prepare_headers(),
            json=provider.prepare_body(messages),
            stream=True
        )
        response.raise_for_status()
        
        # Return the streaming response
        return provider.parse_stream(response)
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]API Error: {str(e)}[/red]")
        return None