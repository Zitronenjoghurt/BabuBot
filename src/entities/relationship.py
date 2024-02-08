from datetime import datetime
from enum import Enum
from typing import Any, Coroutine, Optional
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.utils.discord_time import relative_time
from src.utils.time_operations import get_todays_midnight, get_tomorrows_midnight

class RelationshipAction(Enum):
    GREET = "greet"
    DATE = "date"
    HUG = "hug"
    KISS = "kiss"
    HANDHOLD = "handhold"

ACTION_POINTS = {
    RelationshipAction.GREET: 10,
    RelationshipAction.DATE: 30,
    RelationshipAction.HUG: 100,
    RelationshipAction.KISS: 250,
    RelationshipAction.HANDHOLD: 1000
}

DEFAULT_ACTION = RelationshipAction.GREET
ACTION_UNLOCK = {
    RelationshipAction.GREET: 0,
    RelationshipAction.DATE: 30,
    RelationshipAction.HUG: 150,
    RelationshipAction.KISS: 750,
    RelationshipAction.HANDHOLD: 3000
}

DEFAULT_RANK = "Strangers"
RANK_POINTS = {
    "Strangers": 0,
    "Acquaintances": 30,
    "Friends": 100,
    "Close Friends": 300,
    "Best Friends": 500,
    "Friends with benefits": 750,
    "Lovers": 1500,
    "Soulmates": 3000
}

# An entry in the relationship database, not to be mixed up with the relationships class
class Relationship(AbstractDatabaseEntity):
    TABLE_NAME = "relationships"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "user_ids", "points", "actions"]
    SAVED_PROPERTIES = ["created_stamp", "user_ids", "points", "actions"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            user_ids: Optional[list[str]] = None,
            points: Optional[int] = None,
            actions: Optional[dict[str, dict[str, float]]] = None
        ) -> None:
        super().__init__(id, created_stamp)
        if user_ids is None:
            user_ids = []
        if points is None:
            points = 0
        if actions is None:
            actions = {}

        self.user_ids = user_ids
        self.points = points

        # dict[action_name, (userid, timestamp)]
        # To track what actions have been taken, an action requires 
        # the other party to do the same before points are added
        self.actions = actions

    # Overwrite load method from database base class
    @staticmethod
    async def load(user_ids: list[str]) -> 'Relationship':
        entity = await Relationship.find_containing(key="user_ids", values=user_ids)
        if not entity:
            return Relationship(user_ids=user_ids)
        return entity
    
    def get_unlocked_actions(self) -> list[RelationshipAction]:
        actions = []
        for action, unlock_points in ACTION_UNLOCK.items():
            if self.points >= unlock_points:
                actions.append(action)
        return actions
    
    def get_recently_unlocked_action(self) -> RelationshipAction:
        action = DEFAULT_ACTION
        for current_action, unlock_points in ACTION_UNLOCK.items():
            if self.points >= unlock_points:
                action = current_action
            else:
                break
        return action
    
    def get_next_action(self) -> tuple[str, int]:
        current_action = self.get_recently_unlocked_action()
        actions = list(RelationshipAction)
        current_index = actions.index(current_action)

        if current_index < len(actions) - 1:
            next_action = actions[current_index + 1]
            next_points = ACTION_UNLOCK[next_action]
            return next_action.value, (next_points - self.points)
        else:
            return "highest rank", 0
    
    def get_rank(self) -> str:
        rank = DEFAULT_RANK
        for rank_name, unlock_points in RANK_POINTS.items():
            if self.points >= unlock_points:
                rank = rank_name
            else:
                break
        return rank
    
    def get_next_rank(self) -> tuple[str, int]:
        current_rank = self.get_rank()

        ranks = list(RANK_POINTS.keys())
        current_index = ranks.index(current_rank)
        if current_index < len(ranks) - 1:
            next_rank = ranks[current_index + 1]
            next_points = RANK_POINTS[next_rank]
            return next_rank, (next_points - self.points)
        else:
            return "highest rank", 0

    def get_partner_id(self, user_id: str) -> Optional[str]:
        if user_id not in self.user_ids:
            return None
        return [id for id in self.user_ids if id != user_id][0]
    
    def validate_user_and_action(self, action: RelationshipAction, user_id: str) -> tuple[bool, str]:
        if not isinstance(action, RelationshipAction):
            return False, f"{action} is not a valid action."
        if user_id not in self.user_ids:
            return False, "The user is not part of the relationship."
        return True, ""

    def can_do_action(self, action: RelationshipAction, user_id: str) -> tuple[bool, str]:
        valid, message = self.validate_user_and_action(action=action, user_id=user_id)
        if not valid:
            return False, message
        
        if self.points < ACTION_UNLOCK[action]:
            return False, f"This action is unlocked after you two have reached **`{ACTION_UNLOCK[action]}`** relationship points."
        
        midnight_stamp = get_todays_midnight().timestamp()
        action_entry = self.actions.get(action.value, None)
        if action_entry:
            if user_id in action_entry and len(action_entry) == 1:
                return False, f"Wait for your partner to do the same action on you today!"

            last_stamp = action_entry.get(user_id, 0)
            if midnight_stamp < last_stamp:
                return False, f"Your next `{action.value}` is available {relative_time(int(get_tomorrows_midnight().timestamp()))}"
        else:
            self.actions[action.value] = {}
        return True, ""
    
    # Removes the userid from the actions dict if its timestamp is from yesterday
    def check_action_remove_stamps(self, action: RelationshipAction) -> None:
        if not isinstance(action, RelationshipAction):
            return
        if action.value not in self.actions:
            self.actions[action.value] = {}
        
        midnight_stamp = get_todays_midnight().timestamp()
        remove_userids = []
        for userid, last_stamp in self.actions[action.value].items():
            if midnight_stamp > last_stamp:
                remove_userids.append(userid)
        for remove_userid in remove_userids:
            self.actions[action.value].pop(remove_userid)

    # Userid is the id of the user initiating the action
    def do_action(self, action: RelationshipAction, user_id: str) -> tuple[bool, str]:
        self.check_action_remove_stamps(action=action)

        valid, message = self.can_do_action(action=action, user_id=user_id)
        if not valid:
            return False, message
        
        self.actions[action.value][user_id] = datetime.now().timestamp()
        
        # If length is 2 then both partners have initiated the same action today
        if len(self.actions[action.value]) == 2:
            previous_unlocks = set(self.get_unlocked_actions())
            self.points += ACTION_POINTS[action]
            current_unlocks = set(self.get_unlocked_actions())
            
            message = f"*Both of you have used `{action.value}` on each other today!*\n**Your relationship gained `{ACTION_POINTS[action]}` points!**"
            new_unlocks = current_unlocks - previous_unlocks
            if len(new_unlocks) > 0:
                for unlock in new_unlocks:
                    message += f"\nUnlocked **`{unlock.value}`** action!"

            return True, message
        
        return True, f"**YAY! Now wait for your partner to {action.value} you back :3**\n*After that your relationship will advance!*"
    
    def get_pending(self, user_id: str) -> str:
        if user_id not in self.user_ids:
            return ""
        
        you_id = user_id
        partner_id = self.get_partner_id(user_id=user_id)

        if not partner_id:
            return ""
        
        status = {}
        available_actions = self.get_unlocked_actions()
        for action in available_actions:
            pending = []
            you_pending, _ = self.can_do_action(action=action, user_id=you_id)
            partner_pending, _ = self.can_do_action(action=action, user_id=partner_id)
            if you_pending:
                pending.append("you")
            if partner_pending:
                pending.append("partner")
            status[action.value] = ", ".join(pending)
        
        return "\n".join([f"❥ **{name.capitalize()}**: `{pending if pending else 'DONE'}`" for name, pending in status.items()])