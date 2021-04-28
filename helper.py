import datetime as dt

def render_date():
    now = dt.datetime.now()
    year = now.year
    day = now.day
    month = now.strftime("%B")

    return f"{month} {day}, {year}"