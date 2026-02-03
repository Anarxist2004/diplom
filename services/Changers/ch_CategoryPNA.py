from services.i_dataChanger import IDataChanger
from services.tech_card import TechCardData

class CategoryPNA(IDataChanger):
    def changeData(self,data:TechCardData):
        # for block_key, block in data["params"].items():
        #     if block.get("name") == "Объект контроля":
        # # добавляем новый параметр
        #         next_param_key = str(len(block["params"]) + 1)  # автоматически следующий ключ
        #         block["params"][next_param_key] = {"name": "Язык реализации", "val": "Python"}
        #         print(f'Параметр добавлен в блок "{block_key}"')
        #     break
        # else:
        #     print("Блок с именем 'Объект контроля' не найден")
        return
