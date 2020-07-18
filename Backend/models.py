import os
from urllib.parse import urlparse
from peewee import *  # pylint: disable=unused-wildcard-import
import datetime as dt
import json

from jira import jiraQuery

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
    buildingCode = CharField(primary_key=True)
    buildingName = CharField()
    
    @classmethod
    def createRoom(cls, buildingName, buildingCode):
        try:
            newBuilding = cls.create(
                buildingCode = buildingCode,
                buildingName = buildingName
            )

            return newBuilding
        except IntegrityError:
            raise ValueError(f"Building Already Exists")

# a set of desks
class Space(Base):
    building = ForeignKeyField(CompanyBuildings, backref="spaces")
    spaceName = CharField()
    spaceID = CharField(primary_key=True)

    @classmethod
    def createSpace(cls, spaceName, spaceID, building):
        try:
            newSpace = cls.create(
                building = building,
                spaceName = spaceName,
                spaceID = spaceID
            )

            return newSpace
        except IntegrityError:
            raise ValueError(f"Space Already Exists")

    @property
    def numOfDesks(self):
        desks = (
            Desk.select()
            .where(Desk.spaceID == self.spaceID)
        )

        return desks.count()

class Desk(Base):
    space = ForeignKeyField(Space, backref="desks")
    deskName = CharField()
    deskID = CharField(primary_key=True)

    @classmethod
    def createDesk(cls, deskName, deskID, space):
        try:
            newDesk = cls.create(
                space = space,
                deskName = deskName,
                deskID = f"{space}-{deskName}"
            )

            return newDesk
        except IntegrityError:
            raise ValueError(f"Desk Already Exists")

class Person(Base):
    isPM = BooleanField(default=False)
    personID = CharField(primary_key=True)

    @classmethod
    def createPerson(cls, personID, isPM=False):
        try:
            newPerson = cls.create(
                personID=personID,
                isPM=isPM
            )

            return newPerson
        except IntegrityError:
            raise ValueError(f"Person Already Exists")

class Project(Base):
    projectID = CharField(primary_key=True)
    domain = CharField()

    @classmethod
    def createProject(cls, domain, projectID):
        try:
            newProject = cls.create(
                projectID=projectID,
                domain=domain
            )

            return newProject
        except IntegrityError:
            raise ValueError(f"Project Already Exists")
    
    def getIssueKeys(self, auth):
        path = "/rest/api/3/search"
        query = {
            'jql': f'project = {self.projectID}',
            'fields' : 'key',
        }
        queryObj = jiraQuery(auth, self.domain, path, query=query)
        response = queryObj.send()
        lis = [x["key"] for x in json.loads(response.text)["issues"]]
        return lis

class JiraTicket(Base):
    ticketID = CharField(primary_key=True)
    projectID = ForeignKeyField(Project, backref="tickets")

    @classmethod
    def createTicket(cls, ticketID, projectID):
        try:
            newTicket = cls.create(
                ticketID = ticketID,
                projectID = projectID
            )

            return newTicket
        except IntegrityError:
            raise ValueError(f"Ticket Already Exists")

class ProjectSpaceAllocation(Base):
    allocationDate = DateField()
    space = ForeignKeyField(Space, backref="projectAllocations")
    project = ForeignKeyField(Project, backref="spaceAllocations")

    # Date as a date object
    @classmethod
    def AllocateProjectSpace(cls, space, project, date):
        # DEBUG: make sure date works
        try:
            newAllocation = cls.create(
                allocationDate = date,
                space = space,
                project = project
            )

            return newAllocation
        except IntegrityError:
            raise ValueError(f"Project/Space Allocation Already Exists")

class AllocatedDesk(Base):
    allocationDate = DateField()
    desk = ForeignKeyField(Desk, backref="personAllocations")
    person = ForeignKeyField(Person, backref="deskAllocations")

    # Date as a date object
    @classmethod
    def AllocateDeskToPerson(cls, desk, person, date):
        # DEBUG: make sure date works
        try:
            newAllocation = cls.create(
                allocationDate = date,
                desk = desk,
                person = person
            )

            return newAllocation
        except IntegrityError:
            raise ValueError(f"Person/Desk Allocation Already Exists")

class PersonTickets(Base):
    ticketID = ForeignKeyField(JiraTicket, backref="allocations")
    person = ForeignKeyField(Person, backref="tickets")
    
    @classmethod
    def assignTickets(cls, ticketID, person):
        try:
            newAllocation = cls.create(
                ticketID = ticketID,
                person = person
            )

            return newAllocation
        except IntegrityError:
            raise ValueError(f"Ticket Assign Already Exists")

class PersonProjects(Base):
    projectID = ForeignKeyField(Project, backref="allocations")
    person = ForeignKeyField(Person, backref="projects")
    
    @classmethod
    def assignProjects(cls, projectID, person):
        try:
            newAllocation = cls.create(
                projectID = projectID,
                person = person
            )

            return newAllocation
        except IntegrityError:
            raise ValueError(f"Project Assign Already Exists")

# def dbWipe():
#     modelList = [AllocatedRoom, Student, Room, Floor, SystemInformation]
#     for model in modelList:
#         model.delete().execute() # pylint: disable=no-value-for-parameter

# def db_reset():
#     db.connect()
#     # db.drop_tables([Student, Floor, Room, AllocatedRoom, SystemInformation])
#     db.create_tables([Student, Floor, Room, AllocatedRoom, SystemInformation], safe=True)
#     db.close()