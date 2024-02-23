from src.constants.config import Config
from src.entities.user import User
from src.scrollables.abstract_scrollable_query import AbstractScrollableQuery

CONFIG = Config.get_instance()
PAGE_SIZE = 25

class LevelTopScrollable(AbstractScrollableQuery):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    @staticmethod
    async def create() -> 'LevelTopScrollable':
        return await LevelTopScrollable.create_from_find(
            entity_cls=User,
            page_size=PAGE_SIZE,
            sort_key="levels.total_xp",
        )
    
    async def output(self) -> str:
        users: list[User] = self.get_current_entities()
        if len(users) == 0:
            return "*no users*"
        
        position_offset = PAGE_SIZE * self.current_index + 1
        strings = []
        for i, user in enumerate(users):
            position = i + position_offset
            level = user.levels.get_level()
            _, ratio = user.levels.get_level_progress()
            string = f"#**{position}** ❥ **`{level} ({ratio*100}%)`** | **{user.get_display_name()}**"
            strings.append(string)
        return "\n".join(strings)