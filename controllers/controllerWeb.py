from interfaces.i_controllers import IControllers
from services.tech_card import TechCardData
from interfaces.i_servise import IServise

class ControllerWeb(IControllers[TechCardData]):
    def __init__(self):
        pass

    def setServise(self,serv:IServise):
        serv=serv    
    
    def handle_request(self, data: TechCardData) -> TechCardData:
        """Обрабатывает входные данные и возвращает результат"""
        pass    