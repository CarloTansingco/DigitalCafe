import database as db

def login(username, password):
    error_message = None
    user = None
    temp_user = db.get_user(username)

    if temp_user is not None:
        if temp_user["password"] == password:
            user = {
                "username": username,
                "first_name": temp_user["first_name"],
                "last_name": temp_user["last_name"]
            }
        else:
            error_message = "Invalid password. Please try again."
    else:
        error_message = "Invalid username. Please try again."

    return user, error_message