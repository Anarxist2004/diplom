
from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class PipeLine:
    def __init__(self):
        self.changerArr = []

    def addChanger(self,changer:IDataChanger,index:int ):
        if index < 0:
            raise IndexError("index must be >= 0")
        
        if(len(self.changerArr)>index):
            self.changerArr[index].append(changer)
        elif(len(self.changerArr)==index):
            self.changerArr.append([])
            self.changerArr[index].append(changer)

    def process(self,techCard:TechCardData,index:int):

        if(len(self.changerArr)<index):
            raise IndexError("index must be >= 0")
        
        for changer in self.changerArr[index]:
            changer.changeData(techCard) 

        
