from repositories.postgresDataBase import PostgresDataBase
from services.tech_card_service import TechCardService
from services.tech_card_service import TechCardData
from controllers.controllerWeb import ControllerWeb
from controllers.adapterWeb import create_adapter

test =False
def main():
    
    repo = PostgresDataBase("host=localhost port=5435 dbname=techCard user=postgres password=1")
    controller=ControllerWeb()
    service = TechCardService(repo,controller)
    controller.setServise(service)
    create_adapter(controller)

    
    


def testF():
    repo = PostgresDataBase("host=localhost port=5435 dbname=techCard user=postgres password=1")
    controller=ControllerWeb()
    service = TechCardService(repo,controller)
    controller.setServise(service)
    #create_adapter(controller)

    # tech_data3 = TechCardData({
    #     "typeOfControlledlement": 0,  
    # })
    print(repo.get_all_possible_values_by_param_and_element(1,2 ))
   # print(repo.get_all_controlled_element_types())
    #print(service.findNewParamsByTechCard(tech_data3))
    #print(tech_data3)
    a=0
    a+=1
    
if __name__ == "__main__":
    if(test):
        testF()
    else: 
        main()