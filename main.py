from repositories.postgresDataBase import PostgresDataBase
from services.tech_card_service import TechCardService
from services.tech_card_service import TechCardData
from controllers.controllerWeb import ControllerWeb

test =True
def main():
    
    repo = PostgresDataBase()
    controller=ControllerWeb()
    service = TechCardService(repo,controller)
    controller.setServise(service)


def test():
    repo = PostgresDataBase()
    controller=ControllerWeb()
    service = TechCardService(repo,controller)
    controller.setServise(service)

    # tech_data3 = TechCardData({
    #     "typeOfControlledlement": 0,  
    # })
    
    print(repo.get_available_params_for_type(0))
    #print(service.findNewParamsByTechCard(tech_data3))
    #print(tech_data3)
    a=0
    a+=1
    
if __name__ == "__main__":
    if(test):
        test()
    else: 
        main()