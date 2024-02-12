import json
import sqlite3
from numbers import Number
from typing import Any, Optional
from src.logging.logger import LOGGER
from src.utils.validator import validate_of_type

TABLE_NAMES = ["feedback", "users", "word_analyzer", "relationships"]

class Database():
    _instance = None

    def __init__(self) -> None:
        if Database._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of Database.")
        self.connection = sqlite3.connect("bot.db")
        self.cursor = self.connection.cursor()
        self._setup()

    def _setup(self) -> None:
        for table_name in TABLE_NAMES:
            self.create_table(table_name=table_name)

    @staticmethod
    def get_instance() -> 'Database':
        if Database._instance is None:
            Database._instance = Database()
        return Database._instance
    
    def create_table(self, table_name: str) -> None:
        self.cursor.execute(
            f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
            '''
        )
        self.connection.commit()
    
    def insert(self, table_name: str, data: dict) -> Optional[int]:
        validate_table_name(table_name=table_name)
        json_data = json.dumps(data)
        self.cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (json_data,))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def update(self, table_name: str, entity_id: int, data: dict) -> None:
        validate_table_name(table_name=table_name)
        json_data = json.dumps(data)
        self.cursor.execute(f"UPDATE {table_name} SET data = ? WHERE id = ?", (json_data, entity_id))
        self.connection.commit()

    def find(self, table_name: str, **kwargs) -> Any:
        validate_table_name(table_name=table_name)
        
        conditions = []
        values = []
        for key, value in kwargs.items():
            conditions.append(f"json_extract(data, '$.{key}') = ?")
            values.append(value)
        
        query = " AND ".join(conditions)
        self.cursor.execute(f"SELECT id, data FROM {table_name} WHERE {query}", values)
        return self.cursor.fetchone()
    
    def find_containing(self, table_name: str, key: str, values: list) -> Any:
        validate_table_name(table_name=table_name)
        
        values_part = ", ".join([f"'{value}'" for value in values])
        query = f"SELECT t.id, t.data FROM {table_name} AS t, json_each(t.data, '$.{key}') WHERE json_each.value IN ({values_part}) GROUP BY t.id HAVING Count(DISTINCT json_each.value) = {len(values)};"
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def findall_containing(self, table_name: str, key: str, values: list, sort_key: Optional[str] = None, descending: bool = True, limit: Optional[int] = None, page: int = 1) -> Any:
        validate_of_type(table_name, str, "table_name")
        validate_of_type(descending, bool, "descending")
        validate_of_type(page, Number, "page")
        if sort_key:
            validate_of_type(sort_key, str, "sort_key")
        if limit:
            validate_of_type(limit, Number, "limit")
        validate_table_name(table_name=table_name)

        order_clause = ""
        if sort_key:
            direction = "DESC" if descending else "ASC"
            order_clause = f" ORDER BY json_extract(data, '$.{sort_key}') {direction}"

        limit_clause = ""
        if limit:
            offset = (page - 1) * limit
            limit_clause = f" LIMIT {limit} OFFSET {offset}"
        
        values_part = ", ".join([f"'{value}'" for value in values])
        query = f"""
                SELECT t.id, t.data 
                FROM {table_name} AS t, json_each(t.data, '$.{key}') 
                WHERE json_each.value IN ({values_part}) 
                GROUP BY t.id HAVING Count(DISTINCT json_each.value) = {len(values)}
                {order_clause}
                {limit_clause};
                """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def findall(
            self,
            table_name: str, 
            sort_key: Optional[str] = None, 
            descending: bool = True,
            limit: Optional[int] = None,
            page: int = 1,
            **kwargs
        ) -> Any:
        validate_of_type(table_name, str, "table_name")
        validate_of_type(descending, bool, "descending")
        validate_of_type(page, Number, "page")
        if sort_key:
            validate_of_type(sort_key, str, "sort_key")
        if limit:
            validate_of_type(limit, Number, "limit")
        
        validate_table_name(table_name=table_name)

        conditions = []
        values = []
        for key, value in kwargs.items():
            conditions.append(f"json_extract(data, '$.{key}') = ?")
            values.append(value)

        order_clause = ""
        if sort_key:
            direction = "DESC" if descending else "ASC"
            order_clause = f" ORDER BY json_extract(data, '$.{sort_key}') {direction}"

        limit_clause = ""
        if limit:
            offset = (page - 1) * limit
            limit_clause = f" LIMIT {limit} OFFSET {offset}"

        if conditions:
            query = " AND ".join(conditions)
            self.cursor.execute(f"SELECT id, data FROM {table_name} WHERE {query}{order_clause}{limit_clause}", values)
        else:
            self.cursor.execute(f"SELECT id, data FROM {table_name}{order_clause}{limit_clause}")
        return self.cursor.fetchall()
    
def validate_table_name(table_name: str) -> None:
    if table_name not in TABLE_NAMES:
        raise ValueError(f"Table {table_name} does not exist or is not known to be created by the database.")