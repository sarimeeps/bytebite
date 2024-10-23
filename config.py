import os

def get_database_url():
    env_type = os.getenv('APP_ENV', 'dev')
    database_url = ''

    if env_type == 'dev':
        database_url = os.getenv('DEV_DATABASE_URL')
    elif env_type == 'test':
        database_url = os.getenv('TESTING_DATABASE_URL')
    else:
        raise Exception(f"Unsupported environment type: {env_type}")

    if not database_url:
        raise Exception(f"Database URL not found for environment: {env_type}")
    
    return database_url
