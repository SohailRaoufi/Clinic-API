from datetime import datetime


def get_curr_time() -> str:
    return datetime.today().strftime("%Y-%m-%d")
    



def get_role(user) -> str:
    if user.is_superuser:
        return "ADMIN"
    elif user.is_staff:
        return "STAFF"
    else:
        return "DOCTOR"