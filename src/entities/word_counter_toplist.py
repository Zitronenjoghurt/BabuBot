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