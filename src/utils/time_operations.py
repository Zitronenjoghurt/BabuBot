from datetime import date, datetime, timedelta

def get_todays_midnight() -> datetime:
    today = date.today()
    return datetime.combine(today, datetime.min.time())

def get_tomorrows_midnight() -> datetime:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    return datetime.combine(tomorrow, datetime.min.time())