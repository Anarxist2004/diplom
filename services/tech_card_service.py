from services.tech_card import TechCardData
from interfaces.i_repository import IRepository
from interfaces.i_controllers import IControllers
from interfaces.i_servise import IServise

class TechCardService(IServise):
    def __init__(self, repo: IRepository):
        self.repo = repo

    def findNewParamsByTechCard(self,data: TechCardData)->None:
        self.repo.findParamsByCurentParam(data)
        return

    def setData(self,data: TechCardData)->None:
        pass

    def getObjectControl(self)->TechCardData:
        return self.repo.get_all_controlled_element_types()
    
    def getControlElements(self,id)->TechCardData:
        return self.repo.get_all_objects_by_type_id(id)
    
    def getControlElementParam(self,id)->TechCardData:
        return self.repo.get_available_params_for_type(id)
    
    def getControlElementParamValue(self,idCntlEl,idParam)->TechCardData:
        return self.repo.get_all_possible_values_by_param_and_element(idCntlEl,idParam)
