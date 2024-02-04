import discord
from typing import Optional
from src.utils.guild_operations import retrieve_members

class WordCounterToplist():
    def __init__(self, toplist: dict[str, dict[str, int]]) -> None:
        self.toplist = toplist

    def get_positions(self, user_id: str) -> dict[str, int]:
        positions = {}
        for word, counts in self.toplist.items():
            if user_id not in counts:
                continue
            positions[word] = list(counts.keys()).index(user_id) + 1
        return positions
    
    def get_word_positions(self, word: str) -> dict[str, int]:
        return self.toplist.get(word.lower(), dict())
    
    async def get_word_positions_string(self, guild: discord.Guild, word: str, maximum: int = 20) -> str:
        positions = self.get_word_positions(word=word)
        position_strings = []

        member_ids = [int(userid) for userid in list(positions.keys())]
        members: dict[int, discord.Member] = await retrieve_members(guild=guild, member_ids=member_ids)

        for i, (userid, count) in enumerate(positions.items()):
            if i >= maximum:
                break

            member: Optional[discord.Member] = members.get(int(userid), None)
            if not member:
                name = "NOT FOUND"
            else:
                name = member.display_name
                
            position = i+1
            position_strings.append(f"#**{position}** ❥ **`{count}`** | **{name}**")
        return "\n".join(position_strings)