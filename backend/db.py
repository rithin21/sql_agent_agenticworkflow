from sqlalchemy import create_engine

CURRENT_CONNECTION=None

def set_connection(connection_string:str):
    global CURRENT_CONNECTION
    CURRENT_CONNECTION=connection_string

def get_engine():
    if CURRENT_CONNECTION is None:
        raise Exception("No database connection established.")
    return create_engine(CURRENT_CONNECTION)