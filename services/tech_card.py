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

    def get(self, key: str):
        return self.params.get(key)

    def set(self, key: str, value):
        self.params[key] = value


    def getTypeObjectControl(self,)->TypeObjectControl:
        return self.type
    
    def to_dict(self) -> Dict:
        return {
            "currentParams": self.params,
    }

    def _to_json_dict(self) -> Dict[str, Any]:
        type_val = self.type.value if hasattr(self.type, "value") else self.type
        return {
            "type": type_val,
            "params": self.params,
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

    def has_block_and_param(self,block_name: str,param_name: str) -> bool:
        for block in self.params.values():
            if block.get("name") == block_name:
                # блок найден
                params = block.get("params", {})
                for param in params.values():
                    if param.get("name") == param_name:
                        return True
                return False

        return False

    def has_block(self, block_name: str) -> bool:
        return any(
            block.get("name") == block_name
            for block in self.params.values()
        )        

    def _find_free_id(self, items: Dict[Any, Any]) -> int:
        used_ids = set()

        for k in items.keys():
            if isinstance(k, int):
                used_ids.add(k)
            elif isinstance(k, str) and k.isdigit():
                used_ids.add(int(k))

        new_id = 1
        while new_id in used_ids:
            new_id += 1

        return new_id

    def add_param_to_block(
        self,
        block_name: str,
        param: Dict[str, Any]
    ) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        for block in self.params.values():
            if block.get("name") == block_name:
                params = block.setdefault("params", {})

                # проверяем на дубликат
                for existing in params.values():
                    if existing.get("name") == param["name"]:
                        return False

                free_id = self._find_free_id(params)
                params[free_id] = dict(param)
                return True

        return False
    
    def insert_param_to_block(
        self,
        block_name: str,
        insert_id: int,
        param: Dict[str, Any]
    ) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        for block in self.params.values():
            if block.get("name") == block_name:
                params = block.setdefault("params", {})

                for existing in params.values():
                    if existing.get("name") == param["name"]:
                        return False

                numeric_keys = sorted(
                    k for k in params.keys() if isinstance(k, int)
                )

                for k in reversed(numeric_keys):
                    if k >= insert_id:
                        params[k + 1] = params.pop(k)

                params[insert_id] = dict(param)
                return True

        return False
    
    def _id_to_sort_key(self, key) -> tuple:
        """
        Преобразует id:
        1        -> (1,)
        "2"      -> (2,)
        "1.2"    -> (1, 2)
        "1.2.10" -> (1, 2, 10)
        """
        if isinstance(key, int):
            return (key,)

        if isinstance(key, str):
            try:
                return tuple(int(part) for part in key.split("."))
            except ValueError:
                pass

        # fallback для странных ключей
        return (float("inf"),)
    
    def sort_all_params(self) -> None:
        for block in self.params.values():
            params = block.get("params")
            if not isinstance(params, dict):
                continue

            sorted_items = sorted(
                params.items(),
                key=lambda item: self._id_to_sort_key(item[0])
            )

            block["params"] = dict(sorted_items)