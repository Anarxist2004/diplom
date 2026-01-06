from services.tech_card import TechCardData
from interfaces.i_repository import IRepository
from interfaces.i_controllers import IControllers
from interfaces.i_servise import IServise

class TechCardService(IServise):
    def __init__(self, repo: IRepository,controller: IControllers):
        self.repo = repo
        self.controller=controller

    def findNewParamsByTechCard(self,data: TechCardData)->None:
        self.repo.findParamsByCurentParam(data)
        return

    def setData(self,data: TechCardData)->None:
        pass

    

