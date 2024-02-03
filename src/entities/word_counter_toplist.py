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
    
    def get_word_positions_string(self, word: str, maximum: int = 20) -> str:
        positions = self.get_word_positions(word=word)
        position_strings = []
        for i, (userid, count) in enumerate(positions.items()):
            if i >= maximum:
                break
            position = i+1
            position_strings.append(f"#**{position}** ❥ **`{count}`** | **<@{userid}>**")
        return "\n".join(position_strings)