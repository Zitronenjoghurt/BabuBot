from typing import Optional
from src.scrollables.abstract_scrollable import AbstractScrollable

class AbstractScrollableQuery(AbstractScrollable):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    @classmethod
    async def create_from_find(cls, entity_cls, page_size: int, sort_key: Optional[str] = None, descending: bool = True, **kwargs):
        entities = await entity_cls.findall(
            sort_key=sort_key,
            descending=descending,
            **kwargs
        )
        return await cls.create_from_entities(entities=entities, page_size=page_size)
    
    @classmethod
    async def create_from_containing(cls, entity_cls, key: str, values: list[str], page_size: int, sort_key: Optional[str] = None, descending: bool = True):
        entities = await entity_cls.findall_containing(
            key=key,
            values=values,
            sort_key=sort_key,
            descending=descending
        )
        return await cls.create_from_entities(entities=entities, page_size=page_size)