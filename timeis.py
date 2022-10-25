from datetime import datetime
from timeit import default_timer as timer
from datetime import timedelta


def timeis():
    global blue
    global yellow
    global green
    global red
    global white
    global line
    global orange
    global cyan

    blue = "\033[38;5;33m" #blue
    green = "\033[38;5;34m" #green
    red= "\033[38;5;160m" #red
    yellow = "\033[38;5;220m" #yellow
    white = "\033[38;5;251m" #white
    orange = "\033[38;5;172m" #orange
    cyan = "\033[38;5;14m" #cyan
    line = "-"*40
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    today = now.strftime("%d")
    return (f"{blue}{current_time}{white}")

timeis()
