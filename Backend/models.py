import os
from urllib.parse import urlparse
from peewee import *  # pylint: disable=unused-wildcard-import
from playhouse.shortcuts import model_to_dict
import datetime as dt

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
    personCapacity = IntegerField()
    
    @classmethod
    def createRoom(cls, buildingName, buildingCode, personCapacity):
        try:
            newBuilding = cls.create(
                buildingCode = buildingCode,
                buildingName = buildingName,
                personCapacity = personCapacity
            )

            return newBuilding
        except IntegrityError:
            raise ValueError(f"Building Already Exists")

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

    @classmethod
    def createProject(cls, projectID):
        try:
            newProject = cls.create(
                projectID=projectID
            )

            return newProject
        except IntegrityError:
            raise ValueError(f"Project Already Exists")

class JiraTicket(Base):
    ticketID = CharField(primary_key=True)
    projectID = ForeignKeyField(Project, backref="tickets")
    ticketPriority = IntegerField()
    meetingDate = DateField(null=True)

    @classmethod
    def createTicket(cls, ticketID, projectID, priority):
        try:
            newTicket = cls.create(
                ticketID = ticketID,
                projectID = projectID,
                ticketPriority = priority
            )

            return newTicket
        except IntegrityError:
            raise ValueError(f"Ticket Already Exists")
    
    @property
    def priority(self):
        if (self.ticketPriority == 1):
            # meeting
            return True
        elif (self.ticketPriority == 0):
            #non meeting
            return False
    
    @property
    def ticketDate (self):
        return self.meetingDate
    
    @ticketDate.setter
    def ticketDate(self, newDate):
        self.meetingDate=newDate
        self.save()

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

class MeetingRequest(Base):
    ticketID = ForeignKeyField(JiraTicket, backref="allocations")
    afterDate = DateField()
    beforeDate = DateField()
    highPriority = BooleanField()
    requestFilled = BooleanField(default=False)
    dateAllocated = DateField(null=True)

    @classmethod
    def makeRequest(cls, ticketID,afterDate,  dueDate, priority):
        try:
            newAllocation = cls.create(
                ticketID = ticketID,
                afterDate = afterDate,
                beforeDate = dueDate,
                highPriority = priority
            )

            return newAllocation
        except IntegrityError:
            raise ValueError(f"Ticket Assign Already Exists")
    
    @property
    def allocatedDate(self):
        if self.requestFilled:
            return self.dateAllocated
        
        else:
            return False
    
    @allocatedDate.setter
    def allocatedDate(self, setDate):
        self.requestFilled = True
        self.dateAllocated = setDate
        self.save()

def dbWipe():
    modelList = [CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest]
    for model in modelList:
        model.delete().execute() # pylint: disable=no-value-for-parameter

def db_reset():
    db.connect()
    # db.drop_tables([CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest])
    db.create_tables([CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest], safe=True)
    db.close()

# db_reset()
new=MeetingRequest.makeRequest(1,dt.date.today(), dt.date.today(),True)

print(model_to_dict(new, recurse=False))