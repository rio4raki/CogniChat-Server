import json
from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称，例如 'get_current_weather'"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述，告诉 AI 这个工具是干嘛的"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON Schema 格式的参数定义"""
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """工具的具体执行逻辑"""
        pass

    def to_openai_schema(self):
        """转换为 OpenAI API 需要的格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }