import os

def get_database_url():
    env_type = os.getenv('APP_ENV', '')

    if not env_type:
        raise Exception("No environment found.")
    
    database_url = ""

    if env_type == "dev":
        database_url = os.getenv('DEV_DATABASE_URL','')
    elif env_type == "test":
        database_url = os.getenv('TESTING_DATABASE_URL','')
    if not database_url:
        raise Exception("Database URL not found.")
    
    return database_url