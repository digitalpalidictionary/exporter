""" Modules is a new version of timeis.py without plain escape sequences
"""

from datetime import datetime

def timeis() -> str:
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return (f'[blue]{current_time}[/blue]')
