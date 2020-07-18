import os
from urllib.parse import urlparse
from peewee import Model, IntegrityError, PostgresqlDatabase, SqliteDatabase  # pylint: disable=unused-wildcard-import
from peewee import DateField, BooleanField, CharField, IntegerField, ForeignKeyField
from playhouse.shortcuts import model_to_dict
import datetime as dt
import json

from jira import jiraQuery, apiUser

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
    if (username == "twright" or username == "tdcwr" or username == "tomhill" or username == "rohan"):
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
    personID = CharField(primary_key=True)
    email = CharField()

    @classmethod
    def createPerson(cls, personID, email):
        try:
            newPerson = cls.create(
                personID=personID,
                email=email
            )

            return newPerson
        except IntegrityError:
            raise ValueError(f"Person Already Exists")
    
    @property
    def activeTicketCount(self):
        return (Person.select().join(PersonTickets)
        .where(PersonTickets.ticketID.requestFilled == False)
        .count())

Person.select().where(Person.personID == "Tom Wright")

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
    
    def getTicketKeys(self, auth):
        path = "/rest/api/3/search"
        query = {
            'jql': f'project = {self.projectID}',
            'fields' : 'key',
        }
        queryObj = jiraQuery(auth, self.domain, path, query=query)
        response = queryObj.send()
        lis = [x["key"] for x in json.loads(response.text)["issues"]]
        return lis
    
    def refreshTickets(self, auth):
        print("refreshing tickets")
        for key in self.getTicketKeys(auth):
            try:
                newTicket = JiraTicket.createTicket(key, self.projectID, "", False)
            except ValueError as e:
                print("error is ", e)
                print('done')
                newTicket = JiraTicket.select().where(JiraTicket.ticketID==key).get()
            except Exception as e:
                print("what the fuck was this")
                print(e)
            newTicket.setDeets(auth)

class JiraTicket(Base):
    ticketID = CharField(primary_key=True)
    projectID = ForeignKeyField(Project, backref="tickets")
    name = CharField()
    assigned = BooleanField()

    @classmethod
    def createTicket(cls, ticketID, projectID, name, assigned):
        try:
            newTicket = cls.create(
                ticketID = ticketID,
                projectID = projectID,
                name = name,
                assinged = assigned
            )

            return newTicket
        except IntegrityError:
            raise ValueError(f"Ticket Already Exists")
    
    def getFields(self, fields, auth):
        path = "/rest/api/3/issue/" + self.ticketID
        query = {
            'fields' : ','.join(fields)
        }
        queryObj = jiraQuery(auth, self.projectID.domain, path, query=query)
        response = queryObj.send()
        return json.loads(response.text)
    
    def getWatchers(self, auth):
        path = f"/rest/api/3/issue/{self.ticketID}/watchers"
        queryObj = jiraQuery(auth, self.projectID.domain, path)
        response = queryObj.send()
        data = json.loads(response.text)["watchers"]
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return [{k:i[k] for k in ["accountId", "displayName", "avatarUrls"]} for i in data]
    
    def setDeets(self, auth):
        fields = ['summary']
        data = self.getFields(fields, auth)["fields"]
        self.name = data["summary"]
        self.save()
        print("setting name of", self.ticketID, "to", self.name)
        self.genAttendees(auth)
    
    def genAttendees(self, auth):
        for person in self.getWatchers(auth):
            qry = Person.select().where(Person.personID==person["displayName"])
            if not qry.exists():
                Person.createPerson(person["displayName"], "")
            joinQry = PersonTickets.select().where((PersonTickets.person==person["displayName"]) & (PersonTickets.ticketID==self.ticketID))
            if not joinQry.exists():
                print("assigning ticket", self.ticketID, "to", person["displayName"])
                PersonTickets.assignTickets(self.ticketID, person["displayName"])

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
    def makeRequest(cls, ticketID, afterDate,  dueDate, priority):
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
    def priority(self):
        return self.highPriority

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
    
    def elevatePriority(self):
        self.highPriority = True
        self.save()
    
    @property
    def isActive(self):
        if (self.beforeDate - dt.date.today()).days <=0 and not self.requestFilled:
            return True
        else:
            return False

def dbWipe():
    modelList = [CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest]
    for model in modelList:
        model.delete().execute() # pylint: disable=no-value-for-parameter

def db_reset():
    db.connect()
    # db.drop_tables([CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest])
    db.create_tables([CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest], safe=True)
    # db.close()

try:
    ourProject = Project.createProject("covidspace.atlassian.net", "COV")
except ValueError:
    ourProject = Project.select().where(Project.projectID=="COV").get()
except:
    pass

if __name__ == "__main__":
    #db_reset()
    me = apiUser("rohanmaloney@outlook.com", "lxZVdyemldyTFkmwM5Hn94BD")
    auth = me.getAuth()

    # try:
    #     proj = Project.createProject("covidspace.atlassian.net", "COV")
    # except ValueError:
    #     proj = Project.select().where(Project.projectID=="COV").get()
    # try:
    #     tick = JiraTicket.createTicket("COV-1", "COV")
    # except ValueError:
    #     tick = JiraTicket.select().where(JiraTicket.ticketID=="COV-1").get()

    # print(json.dumps(tick.getWatchers(auth), indent=4, separators=(",", ": ")))

    
def createData():
    
    
    pass