# November 28, 2018 9:01 AM
def default(timestamp: int) -> str:
    return f"<t:{timestamp}>"

# 9:01 AM
def short_time(timestamp: int) -> str:
    return f"<t:{timestamp}:t>"

# 9:01:00 AM
def long_time(timestamp: int) -> str:
    return f"<t:{timestamp}:T>"

# 11/28/2018
def short_date(timestamp: int) -> str:
    return f"<t:{timestamp}:d>"

# November 28, 2018
def long_date(timestamp: int) -> str:
    return f"<t:{timestamp}:D>"

# November 28, 2018 9:01 AM
def short_date_time(timestamp: int) -> str:
    return f"<t:{timestamp}:f>"

# Wednesday, November 28, 2018 9:01 AM
def long_date_time(timestamp: int) -> str:
    return f"<t:{timestamp}:F>"

# 3 years ago
def relative_time(timestamp: int) -> str:
    return f"<t:{timestamp}:R>"