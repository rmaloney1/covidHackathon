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

# Base Peewee class
class Base(Model):
    class Meta:
        database=db

# Stores all offices (can be multiple buildings)
class CompanyBuildings(Base):
    pass

# stores all desk-spaces and conference rooms
class Office(Base):
    pass

# a set of desks
class Space(Base):
    pass

class Desk(Base):
    pass

class Person(Base):
    isPm = True
    personID = 123

class Project(Base):
    pass

class JiraTicket(Base):
    pass

class ProjectSpaceAllocation(Base):
    pass

class AllocatedDesk(Base):
    pass

class PersonTickets(Base):
    pass