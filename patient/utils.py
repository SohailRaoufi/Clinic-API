from datetime import datetime


def get_curr_time() -> str:
    return datetime.today().strftime("%Y-%m-%d")
    
