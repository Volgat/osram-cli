import os
import json
from typing import Dict, Any, Generator
import requests
from rich.console import Console

console = Console()

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
                    data = json.loads(decoded[6:])
                    if "choices" in data and data["choices"]:
                        content = data["choices"][0].get("delta", {}).get("content", "")
                        if content:
                            yield content

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
                    data = json.loads(decoded[6:])
                    if data.get("type") == "content_block_delta":
                        content = data.get("delta", {}).get("text", "")
                        if content:
                            yield content

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
                    data = json.loads(decoded[6:])
                    if "choices" in data and data["choices"]:
                        content = data["choices"][0].get("delta", {}).get("content", "")
                        if content:
                            yield content

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
                    continue

PROVIDERS = {
    "zai": ZhipuProvider,
    "claude": AnthropicProvider,
    "gemini": GoogleProvider,
    "openai": OpenAIProvider,
    "qwen": QwenProvider
}