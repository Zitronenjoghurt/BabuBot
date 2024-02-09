from typing import Optional

class AbstractScrollableQuery():
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        self.page_size = page_size
        self.current_index = starting_page - 1
        self.pages = []
        self.entity_count = 0

    def _clam_index(self) -> None:
        page_count = self.get_page_count()
        if self.current_index >= page_count:
            self.current_index = page_count - 1
        elif self.current_index < 0:
            self.current_index = 0

    def _count_entities(self) -> int:
        count = 0
        for page in self.pages:
            count += len(page)
        return count

    @classmethod
    async def create_from_find(cls, entity_cls, page_size: int, sort_key: Optional[str] = None, descending: bool = True, **kwargs):
        scrollable_query = cls(page_size=page_size)
        entities = await entity_cls.findall(
            sort_key=sort_key,
            descending=descending,
            **kwargs
        )
        scrollable_query.pages = [entities[i:i + page_size] for i in range(0, len(entities), page_size)]
        scrollable_query.entity_count = scrollable_query._count_entities()
        scrollable_query._clam_index()
        return scrollable_query
    
    @classmethod
    async def create_from_containing(cls, entity_cls, key: str, values: list[str], page_size: int, sort_key: Optional[str] = None, descending: bool = True):
        scrollable_query = cls(page_size=page_size)
        entities = await entity_cls.findall_containing(
            key=key,
            values=values,
            sort_key=sort_key,
            descending=descending
        )
        scrollable_query.pages = [entities[i:i + page_size] for i in range(0, len(entities), page_size)]
        scrollable_query.entity_count = scrollable_query._count_entities()
        scrollable_query._clam_index()
        return scrollable_query
    
    @classmethod
    async def output(cls) -> str:
        # To be implemented depending on the child class specifications
        return ""
    
    def get_current_entities(self) -> list:
        try:
            entities = self.pages[self.current_index]
        except IndexError:
            return []
        return entities

    def get_page_count(self) -> int:
        return len(self.pages)
    
    def get_footer(self) -> str:
        return f"page {self.current_index+1}/{self.get_page_count()} | total: {self.entity_count}"
    
    def is_scrollable(self) -> bool:
        return self.entity_count > self.page_size

    async def next(self) -> str:
        page_count = self.get_page_count()
        if page_count == 0:
            self.current_index = 0
            return await self.output()
        
        self.current_index = (self.current_index + 1) % self.get_page_count()
        return await self.output()

    async def previous(self) -> str:
        page_count = self.get_page_count()
        if page_count == 0:
            self.current_index = 0
            return await self.output()
        
        self.current_index = (self.current_index - 1) % self.get_page_count()
        return await self.output()