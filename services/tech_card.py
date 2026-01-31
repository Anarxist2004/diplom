import json
from typing import Optional, Dict, Any

from enum import StrEnum
class TypeObjectControl(StrEnum):
    PLATE="пластина"
    PIPE="труба"
    
class TechCardData:
    def __init__(
        self,
        typeObjectControl: Optional[TypeObjectControl] = None,
        params: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        self.type = typeObjectControl
        self.params = params or {}
        self.available: Dict[str, Any] = {}

    def get(self, key: str):
        return self.params.get(key)

    def set(self, key: str, value):
        self.params[key] = value

    def set_available(self, key: str, value: Any) -> None:
        """Установить доступные значения для параметра."""
        self.available[key] = value

    def getTypeObjectControl(self,)->TypeObjectControl:
        return self.type
    
    def to_dict(self) -> Dict:
        return {
            "current": self.params,
            "available": self.available
    }

    def _to_json_dict(self) -> Dict[str, Any]:
        type_val = self.type.value if hasattr(self.type, "value") else self.type
        return {
            "type": type_val,
            "params": self.params,
            "available": self.available,
        }

    def __str__(self) -> str:
        return json.dumps(
            self._to_json_dict(),
            ensure_ascii=False,
            indent=2,
        )

    def serialise(self) -> str:
        return json.dumps(
            self._to_json_dict(),
            ensure_ascii=False,
            indent=2,
        )
        

