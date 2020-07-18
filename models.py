import os
from urllib.parse import urlparse
from peewee import *  # pylint: disable=unused-wildcard-import

if "HEROKU" in os.environ:
    url = urlparse(os.environ["DATABASE_URL"])
    db = PostgresqlDatabase(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )
else:
    
    import getpass
    username = getpass.getuser()
    if (username == "twright" or username == "tdcwr" or username == "tomhill"):
        db = SqliteDatabase('test1.db')
    else:
        from dotenv import load_dotenv # pylint: disable=import-error
        load_dotenv()
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        db_pword = os.environ["DB_PASSWORD"]
        db = PostgresqlDatabase(db_name, user=db_user, password=db_pword)
