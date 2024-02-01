import json
import sqlite3
from typing import Any, Optional

class Database():
    _instance = None

    def __init__(self) -> None:
        if Database._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of Database.")
        self.connection = sqlite3.connect("bot.db")
        self.cursor = self.connection.cursor()

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
        json_data = json.dumps(data)
        self.cursor.execute(f"INSERT INTO {table_name} (data) VALUES (?)", (json_data,))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def update(self, table_name: str, entity_id: int, data: dict) -> None:
        json_data = json.dumps(data)
        self.cursor.execute(f"UPDATE {table_name} SET data = ? WHERE id = ?", (json_data, entity_id))
        self.connection.commit()
        
    def find(self, table_name: str, **kwargs) -> Any:
        conditions = []
        values = []
        for key, value in kwargs.items():
            conditions.append(f"json_extract(data, '$.{key}') = ?")
            values.append(value)
        
        query = " AND ".join(conditions)
        self.cursor.execute(f"SELECT id, data FROM {table_name} WHERE {query}", values)
        return self.cursor.fetchall()