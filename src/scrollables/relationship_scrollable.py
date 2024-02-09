from src.entities.relationship import Relationship
from src.entities.user import User
from src.scrollables.abstract_scrollable_query import AbstractScrollableQuery

PAGE_SIZE = 20

class RelationshipScrollable(AbstractScrollableQuery):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        self.user_id: str = ""
        super().__init__(page_size, starting_page)

    def set_user_id(self, user_id: str) -> None:
        self.user_id = user_id

    @staticmethod
    async def create(user_ids: list[str]) -> 'RelationshipScrollable':
        return await RelationshipScrollable.create_from_containing(
            entity_cls=Relationship,
            key="user_ids",
            values=user_ids,
            page_size=PAGE_SIZE,
            sort_key="points"
        )
    
    async def output(self) -> str:
        if len(self.user_id) == 0:
            return "An unexpected error occured: userid for scrollable not set"
        
        relationships: list[Relationship] = self.get_current_entities()
        if len(relationships) == 0:
            return "*no relationships*"
        
        strings = []
        for relationship in relationships:
            partner_id = relationship.get_partner_id(self.user_id)
            if not partner_id:
                continue
            partner: User = await User.load(userid=partner_id)
            string = f"❥ **`({relationship.points}) {relationship.get_rank()}`** x **{partner.get_display_name()}** | `{relationship.get_pending_status()}`"
            strings.append(string)
        return "\n".join(strings)