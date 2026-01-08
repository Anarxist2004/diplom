from interfaces.i_repository import IRepository
from services.tech_card import TechCardData
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor



class PostgresDataBase(IRepository[TechCardData]):
    def __init__(self,dsn):
        try:
            
            # создаем подключение
            self.conn = psycopg2.connect(dsn)


            # курсор с возвратом строк как словарей
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Подключение к базе успешно")
        except psycopg2.Error as e:
            print("Ошибка при подключении к базе:", e)
            self.conn = None
            self.cursor = None

    def add(self, entity: TechCardData) -> None:
        self._cards.append(entity)

    def update(self, entity: TechCardData) -> None:
        for i, card in enumerate(self._cards):
            if card.id == entity.id:
                self._cards[i] = entity

    def delete(self, entity: TechCardData) -> None:
        self._cards = [c for c in self._cards if c.id != entity.id]

    def get_by_id(self, id: int) -> TechCardData | None:
        for card in self._cards:
            if card.id == id:
                return card
        return None

    def list_all(self) -> list[TechCardData]:
        return self._cards
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()

    def findParamsByCurentParam(self, data: TechCardData):
        """
        Find available parameters based on current parameters.
        """
        try:
            current_params = data.params
            
            print(f"DEBUG: Current params: {current_params}")
            
            query_conditions = []
            query_params = []
            
            # Filter by type
            type_control_id = current_params.get('typeOfControlledElement')
            if type_control_id is not None:
                print(f"DEBUG: Filtering by type ID: {type_control_id}")
                query_conditions.append("oc.\"idTypeControl\" = %s")
                query_params.append(type_control_id)
            
            # Filter by other parameters
            if current_params:
                param_subqueries = []
                
                for param_name, param_value in current_params.items():
                    if param_name == 'typeOfControlledElement':
                        continue
                    
                    print(f"DEBUG: Filtering by parameter: {param_name} = {param_value}")
                    
                    self.cursor.execute("""
                        SELECT id FROM "paramsDefinition" 
                        WHERE name = %s
                    """, (param_name,))
                    
                    param_def_result = self.cursor.fetchone()
                    if param_def_result:
                        param_def_id = param_def_result['id']
                        
                        param_subqueries.append(f"""
                            EXISTS (
                                SELECT 1 FROM "paramsObjectControl" poc
                                WHERE poc."idObjectControl" = oc.id
                                AND poc."idDefParams" = %s
                                AND (
                                    (poc."valueInt" = %s)
                                    OR (poc."valueDouble" = %s)
                                    OR (poc."valueString" = %s)
                                    OR (poc."valueBool" = %s)
                                )
                            )
                        """)
                        
                        query_params.extend([
                            param_def_id,
                            param_value if isinstance(param_value, int) else None,
                            param_value if isinstance(param_value, float) else None,
                            param_value if isinstance(param_value, str) else None,
                            param_value if isinstance(param_value, bool) else None
                        ])
                
                if param_subqueries:
                    query_conditions.append("(" + " AND ".join(param_subqueries) + ")")
            
            # Build main query
            query = """
                SELECT oc.id, oc.name, oc."idTypeControl", tce.name as type_name
                FROM "objectControl" oc
                JOIN "typeOfControlledElement" tce ON oc."idTypeControl" = tce."Id"
            """
            
            if query_conditions:
                query += " WHERE " + " AND ".join(query_conditions)
            
            print(f"DEBUG: Query: {query}")
            print(f"DEBUG: Query params: {query_params}")
            
            self.cursor.execute(query, query_params)
            matching_objects = self.cursor.fetchall()
            
            print(f"DEBUG: Found objects: {len(matching_objects)}")
            for obj in matching_objects:
                print(f"  - ID: {obj['id']}, Name: {obj['name']}, Type ID: {obj['idTypeControl']}, Type Name: {obj['type_name']}")
            
            if not matching_objects:
                return data
            
            # Get object IDs
            object_ids = [obj['id'] for obj in matching_objects]
            print(f"DEBUG: Object IDs to search params for: {object_ids}")
            
            # Get parameters ONLY for these objects
            self.cursor.execute("""
                SELECT 
                    pd.name as param_name,
                    pd."typeData",
                    poc."valueInt",
                    poc."valueDouble",
                    poc."valueString",
                    poc."valueBool",
                    oc."idTypeControl"  -- Добавляем тип элемента
                FROM "paramsObjectControl" poc
                JOIN "paramsDefinition" pd ON poc."idDefParams" = pd.id
                JOIN "objectControl" oc ON poc."idObjectControl" = oc.id  -- JOIN с objectControl
                WHERE poc."idObjectControl" = ANY(%s)
                ORDER BY pd.name
            """, (object_ids,))
            
            all_params = self.cursor.fetchall()
            print(f"DEBUG: Found parameters: {len(all_params)} rows")
            
            # Group parameter values by parameter name
            param_values = {}
            for row in all_params:
                param_name = row['param_name']
                type_data = row['typeData']
                v_int = row['valueInt']
                v_double = row['valueDouble']
                v_string = row['valueString']
                v_bool = row['valueBool']
                obj_type_id = row['idTypeControl']  # Получаем тип элемента
                
                print(f"DEBUG: Param '{param_name}' from object type {obj_type_id}")
                
                # Проверяем, что параметр принадлежит нужному типу
                if type_control_id is not None and obj_type_id != type_control_id:
                    print(f"  WARNING: Skipping - object type {obj_type_id} != filter type {type_control_id}")
                    continue
                
                # Extract value
                if type_data.lower() == 'int' and v_int is not None:
                    value = v_int
                elif type_data.lower() == 'double' and v_double is not None:
                    value = v_double
                elif type_data.lower() == 'string' and v_string is not None:
                    value = v_string
                elif type_data.lower() == 'bool' and v_bool is not None:
                    value = v_bool
                else:
                    continue
                
                if param_name not in param_values:
                    param_values[param_name] = set()
                param_values[param_name].add(value)
            
            # Find all types
            self.cursor.execute("""
                SELECT "Id", name FROM "typeOfControlledElement" ORDER BY "Id"
            """)
            type_options = self.cursor.fetchall()
            
            print(f"DEBUG: All types in DB: {type_options}")
            
            # Update available parameters
            for param_name, values_set in param_values.items():
                values_list = sorted(list(values_set))
                data.set_available(param_name, values_list)
                print(f"DEBUG: Setting available {param_name}: {values_list}")
            
            # Add type options
            if type_options:
                type_list = [{"id": t['Id'], "name": t['name']} for t in type_options]
                data.set_available("typeOfControlledElement", type_list)
            
            return data
            
        except Exception as e:
            print(f"Error in findParamsByCurentParam: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            raise

    
    def getParamDefinitions(self) -> List[dict]:
        """Get all parameter definitions"""
        try:
            self.cursor.execute("""
                SELECT id, name, "typeData"
                FROM "paramsDefinition"
                ORDER BY name
            """)
            params = self.cursor.fetchall()
            return [{"id": p[0], "name": p[1], "type": p[2]} for p in params]
        except Exception as e:
            print(f"Error in getParamDefinitions: {e}")
            return []

    def get_available_params_for_type(self, type_id):
        """
        Получить доступные параметры для типа контролируемого элемента
        
        Args:
            type_id (int): ID типа контролируемого элемента
            
        Returns:
            list: Список доступных параметров
        """
        query = """
        SELECT pd.id, pd.name, pd."typeData"
        FROM public."paramsDefinition" pd
        INNER JOIN public."typeParams" tp ON pd.id = tp."idTypeDefParam"
        WHERE tp."idTypeControlEl" = %s
        ORDER BY pd.name;
        """
        self.cursor.execute(query, (type_id,))
        rows = self.cursor.fetchall()
        print(rows)
        id_name_dict = {row['id']: row['name'] for row in rows}
        
        tech_card = TechCardData()
        tech_card.available = id_name_dict
        return tech_card
    
    def get_all_controlled_element_types(self)->TechCardData:
        """
        Получить все типы контролируемых элементов
        
        Returns:
            list: Список всех типов контролируемых элементов
        """
        query = """
        SELECT "Id" as id, name
        FROM public."typeOfControlledElement"
        ORDER BY name;
        """
        self.cursor.execute(query)
        
        rows = self.cursor.fetchall()
        id_name_dict = {row['id']: row['name'] for row in rows}
        
        tech_card = TechCardData()
        tech_card.available = id_name_dict

        return tech_card
    
    def get_all_objects_by_type_id(self, type_id):
        """
        Получить только имена элементов контроля по ID типа
        
        Args:
            type_id (int): ID типа из typeOfControlledElement
            
        Returns:
            list: Имена элементов этого типа
        """
        query = """
        SELECT 
            id,
            name
        FROM public."objectControl"
        WHERE "idTypeControl" = %s
        ORDER BY name
        """
        self.cursor.execute(query, (type_id,))
        rows = self.cursor.fetchall()
        id_name_dict = {row['id']: row['name'] for row in rows}
        tech_card = TechCardData()
        tech_card.available = id_name_dict
        return tech_card
    
    
    def get_all_possible_values_by_param_and_element(self, element_type_id,param_id ):
        #element_type_id,param_id=param_id,element_type_id
        """
        Получить все возможные значения параметра для типа контролируемого элемента
        
        Args:
            param_id (int): ID параметра из paramsDefinition
            element_type_id (int): ID типа контролируемого элемента
            
        Returns:
            list: Все уникальные значения параметра
        """
        # Сначала получаем тип данных параметра
        type_query = """
        SELECT "typeData" 
        FROM public."paramsDefinition" 
        WHERE id = %s
        """
        self.cursor.execute(type_query, (param_id,))
        result = self.cursor.fetchone()
        
        if not result:
            return []
        
        param_type = result['typeData']
        
        # Формируем запрос с правильными именами столбцов
        query = """
        SELECT DISTINCT 
            CASE 
                WHEN poc."valueInt" IS NOT NULL THEN poc."valueInt"::text
                WHEN poc."valueDouble" IS NOT NULL THEN poc."valueDouble"::text
                WHEN poc."valueString" IS NOT NULL THEN poc."valueString"
                WHEN poc."valueBool" IS NOT NULL THEN poc."valueBool"::text
            END as value,
            CASE 
                WHEN poc."valueInt" IS NOT NULL THEN 'integer'
                WHEN poc."valueDouble" IS NOT NULL THEN 'double'
                WHEN poc."valueString" IS NOT NULL THEN 'string'
                WHEN poc."valueBool" IS NOT NULL THEN 'boolean'
            END as value_type
        FROM public."paramsObjectControl" poc
        INNER JOIN public."objectControl" oc ON poc."idObjectControl" = oc.id
        WHERE poc."idDefParams" = %s 
            AND oc."idTypeControl" = %s
        ORDER BY value
        """
        
        self.cursor.execute(query, (param_id, element_type_id))
        all_values = self.cursor.fetchall()
        
        # Преобразуем значения
        processed_values = []
        for item in all_values:
            value = item['value']
            value_type = item['value_type']
            
            if value is None:
                continue
                
            try:
                if param_type.lower() == 'integer' and value_type == 'integer':
                    processed_values.append(int(value))
                elif param_type.lower() in ['double', 'float', 'real'] and value_type in ['double', 'integer']:
                    processed_values.append(float(value))
                elif param_type.lower() == 'boolean' and value_type == 'boolean':
                    processed_values.append(value.lower() == 'true')
                elif param_type.lower() == 'string' and value_type in ['string', 'integer', 'double', 'boolean']:
                    processed_values.append(str(value))
            except (ValueError, TypeError) as e:
                print(f"Ошибка преобразования значения {value}: {e}")
                continue
        
        # Убираем дубликаты и возвращаем
        unique_values = []
        for val in processed_values:
            if val not in unique_values:
                unique_values.append(val)
        
        tech_card = TechCardData()
        tech_card.available = {param_id:unique_values}

        return tech_card