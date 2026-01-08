import json
from typing import Optional

class TechCardData:
    def __init__(self, params: dict | None = None):
        # текущие параметры пользователя
        self.params: dict = params or {}

        # найденные / возможные параметры
        self.available: dict = {}

    def get(self, key: str):
        return self.params.get(key)

    def set(self, key: str, value):
        self.params[key] = value

    def set_available(self, key: str, values: list):
        self.available[key] = values

    
    def to_dict(self) -> dict:
        return {
            "current": self.params,
            "available": self.available
    }

    def __str__(self):
        # Преобразуем словарь в читаемую строку
        data = self.to_dict()
        current = '\n'.join(f"{k}: {v}" for k, v in data["current"].items())
        available = '\n'.join(f"{k}: {v}" for k, v in data["available"].items())
        return f"Current:\n{current}\n\nAvailable:\n{available}"
    
    def serialise(self)->str:
        return json.dumps({
            "params": self.params,
            "available": self.available
        }, ensure_ascii=False, indent=2)
        
    
