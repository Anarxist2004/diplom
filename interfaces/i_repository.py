from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abstractmethod
    def update(self, entity: T) -> None:
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        pass

    @abstractmethod
    def findParamsByCurentParam(self, data: T):
        pass

    @abstractmethod
    def get_available_params_for_type(self, type_id):#получение всех типов контролирующего элемента
        pass

    @abstractmethod
    def get_all_controlled_element_types(self):#получение всех типов контролируемых эементов
        pass

    
