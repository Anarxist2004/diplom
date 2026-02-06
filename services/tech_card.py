import json
from typing import Optional, Dict, Any
from typing import Union

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

    def from_jsonDeSerialise(self, data: str | Dict[str, Any]) -> "TechCardData":
        if isinstance(data, str):
            data = json.loads(data)  # превращаем JSON-строку в словарь

        type_val = data.get("type")
        params = data.get("params", {})


        self.typeObjectControl=type_val
        self.params=params
    
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
    
    def insert_param_to_block(self, block_name: str, insert_id: int, param: Dict[str, Any]) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        for block in self.params.values():
            if block.get("name") != block_name:
                continue

            params = block.setdefault("params", {})

            # Проверка на дубликат по имени
            for existing in params.values():
                if existing.get("name") == param["name"]:
                    return False

            idx = insert_id
            to_move = []

            # Находим цепочку занятых ключей подряд, начиная с insert_id
            while idx in params:
                to_move.append(idx)
                idx += 1

            # Сдвигаем только цепочку занятых ключей
            for k in reversed(to_move):
                params[k + 1] = params.pop(k)

            # Вставляем новый параметр
            params[insert_id] = dict(param)
            return True

        return False
    
    def insert_param_to_block_reWrite(self, block_name: str, insert_id: int, param: Dict[str, Any]) -> bool:
        if "name" not in param:
            raise ValueError("param должен содержать ключ 'name'")

        for block in self.params.values():
            if block.get("name") != block_name:
                continue

            params = block.setdefault("params", {})

            # 1. Проверяем, есть ли параметр с таким же name
            old_key = None
            for k, existing in params.items():
                if existing.get("name") == param["name"]:
                    old_key = k
                    break

            old_key_found = old_key is not None
            
            # 2. Если нашли старый — удаляем
            if old_key_found:
                params.pop(old_key)
                
                # Корректируем insert_id только если old_key был целым числом
                if isinstance(old_key, int) and old_key < insert_id:
                    insert_id -= 1

                # Сдвигаем только целочисленные ключи, которые больше old_key
                if isinstance(old_key, int):
                    sorted_int_keys = sorted(k for k in params if isinstance(k, int))
                    for k in sorted_int_keys:
                        if k > old_key:
                            # Ищем ближайший свободный ключ слева
                            new_key = k - 1
                            while new_key in params or new_key == old_key:
                                new_key -= 1
                            if new_key not in params:
                                params[new_key] = params.pop(k)

            # 3. Сдвигаем хвост вправо только для целочисленных ключей, начиная с insert_id
            # Собираем все целочисленные ключи >= insert_id
            int_keys_greater_equal = []
            for k in params.keys():
                if isinstance(k, int) and k >= insert_id:
                    int_keys_greater_equal.append(k)
            
            # Сортируем по убыванию и сдвигаем
            for k in sorted(int_keys_greater_equal, reverse=True):
                # Ищем ближайший свободный ключ справа
                new_key = k + 1
                while new_key in params:
                    new_key += 1
                params[new_key] = params.pop(k)

            # 4. Вставляем новый параметр
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

    def get_param_value(self,block_name: str,param_name: str) -> Optional[Any]:
        for block in self.params.values():
            if block.get("name") == block_name:
                params = block.get("params", {})
                for param in params.values():
                    if param.get("name") == param_name:
                        return param.get("val")
                return None
        return None
    
    def _parse_id(self, key) -> list[int]:
        if isinstance(key, int):
            return [key]
        if isinstance(key, str):
            return [int(p) for p in key.split(".") if p.isdigit()]
        return []
    
    def _same_level(self, a: list[int], b: list[int]) -> bool:
        return len(a) == len(b)
    
    def change_param_id_by_name_autoshift(
        self,
        block_name: str,
        param_name: str,
        new_id: Union[int, str]
    ) -> bool:
        target_id = self._parse_id(new_id)

        for block in self.params.values():
            if block.get("name") != block_name:
                continue

            params = block.get("params", {})
            old_key = None
            old_id = None

            # ищем параметр по имени
            for k, v in params.items():
                if v.get("name") == param_name:
                    old_key = k
                    old_id = self._parse_id(k)
                    break

            if old_key is None:
                return False  # параметр не найден

            # проверка: параметр уже на нужном месте
            if old_id == target_id:
                return True  # ничего не делаем

            # собираем id того же уровня
            level_keys = []
            for k in params.keys():
                parsed = self._parse_id(k)
                if self._same_level(parsed, target_id):
                    level_keys.append((k, parsed))

            # сдвигаем в обратном порядке
            for k, parsed in sorted(level_keys, key=lambda x: x[1], reverse=True):
                if parsed >= target_id:
                    new_key = ".".join(str(p) for p in (parsed[:-1] + [parsed[-1] + 1]))
                    params[new_key] = params.pop(k)

            # вставляем параметр
            params[".".join(str(p) for p in target_id)] = params.pop(old_key)

            # сортируем после операции
            sorted_items = sorted(
                params.items(), key=lambda item: self._id_to_sort_key(item[0])
            )
            block["params"] = dict(sorted_items)
            return True

        return False
    
    def hasSpecParam(self,block_name: str,param_name: str):
        val = self.get_param_value(block_name, param_name)
    
        # если пустое поле (None) или массив (list/tuple) — False
        if val is None or isinstance(val, (list, tuple)):
            return False
        
        # иначе не массив — True
        return True
        