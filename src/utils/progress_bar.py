EMPTY = "▱"
FULL = "▰"

def progress_bar(current: int, start: int, end: int, length: int) -> tuple[str, float]:
    current = max(start, min(current, end))
    
    progress_ratio = (current - start) / (end - start) if end - start > 0 else 0
    
    full_blocks = int(progress_ratio * length)
    empty_blocks = length - full_blocks
    
    progress_bar_str = FULL * full_blocks + EMPTY * empty_blocks
    
    return progress_bar_str, round(progress_ratio, 2)