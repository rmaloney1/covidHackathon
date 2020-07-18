import os
from urllib.parse import urlparse
from peewee import (
    Model,
    IntegrityError,
    PostgresqlDatabase,
    SqliteDatabase,
)  # pylint: disable=unused-wildcard-import
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
    if (
        username == "twright"
        or username == "tdcwr"
        or username == "tomhill"
        or username == "rohan"
        or username == "tom"
    ):
        db = SqliteDatabase("test1.db")
    else:
        from dotenv import load_dotenv  # pylint: disable=import-error

        load_dotenv()
        db_name = os.environ["DB_NAME"]
        db_user = os.environ["DB_USER"]
        db_pword = os.environ["DB_PASSWORD"]
        db = PostgresqlDatabase(db_name, user=db_user, password=db_pword)

# Base Peewee class
class Base(Model):
    class Meta:
        database = db


# Stores all offices (can be multiple buildings)
class CompanyBuildings(Base):
    buildingCode = CharField(primary_key=True)
    buildingName = CharField()
    personCapacity = IntegerField()

    @classmethod
    def createRoom(cls, buildingName, buildingCode, personCapacity):
        try:
            newBuilding = cls.create(
                buildingCode=buildingCode,
                buildingName=buildingName,
                personCapacity=personCapacity,
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
            newPerson = cls.create(personID=personID, email=email)

            return newPerson
        except IntegrityError:
            raise ValueError(f"Person Already Exists")

    @property
    def activeTicketCount(self):
        return (
            Person.select()
            .join(PersonTickets)
            .where(PersonTickets.ticketID.requestFilled == False)
            .count()
        )


Person.select().where(Person.personID == "Tom Wright")


class Project(Base):
    projectID = CharField(primary_key=True)
    domain = CharField()

    @classmethod
    def createProject(cls, domain, projectID):
        try:
            newProject = cls.create(projectID=projectID, domain=domain)

            return newProject
        except IntegrityError:
            raise ValueError(f"Project Already Exists")

    def getTicketKeys(self, auth):
        path = "/rest/api/3/search"
        query = {
            "jql": f"project = {self.projectID}",
            "fields": "key",
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
                print("done")
                newTicket = JiraTicket.select().where(JiraTicket.ticketID == key).get()
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
    def createTicket(cls, ticketID, projectID, name, assigned=False):
        try:
            newTicket = cls.create(
                ticketID=ticketID, projectID=projectID, name=name, assigned=assigned
            )

            return newTicket
        except IntegrityError:
            raise ValueError(f"Ticket Already Exists")

    def getFields(self, fields, auth):
        path = "/rest/api/3/issue/" + self.ticketID
        query = {"fields": ",".join(fields)}
        queryObj = jiraQuery(auth, self.projectID.domain, path, query=query)
        response = queryObj.send()
        return json.loads(response.text)

    def getWatchers(self, auth):
        path = f"/rest/api/3/issue/{self.ticketID}/watchers"
        queryObj = jiraQuery(auth, self.projectID.domain, path)
        response = queryObj.send()
        data = json.loads(response.text)["watchers"]
        print(
            json.dumps(
                json.loads(response.text),
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
        )
        return [
            {k: i[k] for k in ["accountId", "displayName", "avatarUrls"]} for i in data
        ]

    def setDeets(self, auth):
        fields = ["summary"]
        data = self.getFields(fields, auth)["fields"]
        self.name = data["summary"]
        self.save()
        print("setting name of", self.ticketID, "to", self.name)
        self.genAttendees(auth)

    def genAttendees(self, auth):
        for person in self.getWatchers(auth):
            qry = Person.select().where(Person.personID == person["displayName"])
            if not qry.exists():
                Person.createPerson(person["displayName"], "")
            joinQry = PersonTickets.select().where(
                (PersonTickets.person == person["displayName"])
                & (PersonTickets.ticketID == self.ticketID)
            )
            if not joinQry.exists():
                print("assigning ticket", self.ticketID, "to", person["displayName"])
                PersonTickets.assignTickets(self.ticketID, person["displayName"])


class PersonTickets(Base):
    ticketID = ForeignKeyField(JiraTicket, backref="allocations")
    person = ForeignKeyField(Person, backref="tickets")

    @classmethod
    def assignTickets(cls, ticketID, person):
        try:
            newAllocation = cls.create(ticketID=ticketID, person=person)

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
    def makeRequest(cls, ticketID, afterDate, dueDate, priority):
        try:
            newAllocation = cls.create(
                ticketID=ticketID,
                afterDate=afterDate,
                beforeDate=dueDate,
                highPriority=priority,
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
        if (self.beforeDate - dt.date.today()).days <= 0 and not self.requestFilled:
            return True
        else:
            return False


def dbWipe():
    modelList = [
        CompanyBuildings,
        Person,
        Project,
        JiraTicket,
        PersonTickets,
        MeetingRequest,
    ]
    for model in modelList:
        model.delete().execute()  # pylint: disable=no-value-for-parameter


def db_reset():
    db.connect()
    # db.drop_tables([CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest])
    db.create_tables(
        [CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest],
        safe=True,
    )
    # db.close()


try:
    db_reset()
    ourProject = Project.createProject("covidspace.atlassian.net", "COV")
except ValueError:
    ourProject = Project.select().where(Project.projectID == "COV").get()
except Exception as e:
    print("whaaa", e)
    pass
qry = CompanyBuildings.select()
if not qry.exists():
    CompanyBuildings.createRoom("devonshire", "DEV", 10)
if __name__ == "__main__":
    
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
    CompanyBuildings.createRoom("Building A", "Building A", 10)

    Person.createPerson("Bessie Oakley", "Email1@gmail.com")
    Person.createPerson("Aaron Bryant", "Email2@gmail.com")
    Person.createPerson("Lester Hayward", "Email3@gmail.com")
    Person.createPerson("Asim Hobbs", "Email4@gmail.com")
    Person.createPerson("Harvie Betts", "Email5@gmail.com")
    Person.createPerson("Polly Findlay", "Email6@gmail.com")
    Person.createPerson("Philippa Rocha", "Email7@gmail.com")
    Person.createPerson("Rajveer Wright", "Email8@gmail.com")
    Person.createPerson("Zain Li", "Email9@gmail.com")
    Person.createPerson("Isobel Landry", "Email10@gmail.com")
    Person.createPerson("Myrtle Schroeder", "Email11@gmail.com")
    Person.createPerson("Gracie Byrd", "Email12@gmail.com")
    Person.createPerson("Ariana Bevan", "Email13@gmail.com")
    Person.createPerson("Sameeha Bowers", "Email14@gmail.com")
    Person.createPerson("Luc Fletcher", "Email15@gmail.com")
    Person.createPerson("Fred Gallagher", "Email16@gmail.com")
    Person.createPerson("Sneha Marsh", "Email17@gmail.com")
    Person.createPerson("Isha Wilson", "Email18@gmail.com")
    Person.createPerson("Cassie Mccartney", "Email19@gmail.com")
    Person.createPerson("Bea Key", "Email20@gmail.com")
    Person.createPerson("Nela Hoffman", "Email21@gmail.com")
    Person.createPerson("Ihsan Vu", "Email22@gmail.com")
    Person.createPerson("Ivy Ayala", "Email23@gmail.com")
    Person.createPerson("Aasiyah Mata", "Email24@gmail.com")
    Person.createPerson("Esmai Clark", "Email25@gmail.com")
    Person.createPerson("Isla Good", "Email26@gmail.com")
    Person.createPerson("Arman Yoder", "Email27@gmail.com")
    Person.createPerson("Meerab Hills", "Email28@gmail.com")
    Person.createPerson("Brandi Davey", "Email29@gmail.com")
    Person.createPerson("Kaitlyn Pineda", "Email30@gmail.com")

    Project.createProject("projectSet", "Extra-Project")

    JiraTicket.createTicket("PAJ-1", "Extra-Project", "Absolute electrode potential")
    JiraTicket.createTicket("PAJ-2", "Extra-Project", "Absolute pressure")
    JiraTicket.createTicket("PAJ-3", "Extra-Project", "Absolute zero")
    JiraTicket.createTicket("PAJ-4", "Extra-Project", "Absorbance")
    JiraTicket.createTicket("PAJ-5", "Extra-Project", "AC power")
    JiraTicket.createTicket("PAJ-6", "Extra-Project", "Acceleration")
    JiraTicket.createTicket("PAJ-7", "Extra-Project", "Acid")
    JiraTicket.createTicket("PAJ-8", "Extra-Project", "Acid-base reaction")
    JiraTicket.createTicket("PAJ-9", "Extra-Project", "Acid strength")
    JiraTicket.createTicket("PAJ-10", "Extra-Project", "Acoustics")
    JiraTicket.createTicket("PAJ-11", "Extra-Project", "Activated sludge")
    JiraTicket.createTicket("PAJ-12", "Extra-Project", "Activated sludge model")
    JiraTicket.createTicket("PAJ-13", "Extra-Project", "Active transport")
    JiraTicket.createTicket("PAJ-14", "Extra-Project", "Actuator")
    JiraTicket.createTicket("PAJ-15", "Extra-Project", "Adenosine triphosphate")
    JiraTicket.createTicket("PAJ-16", "Extra-Project", "Adhesion")
    JiraTicket.createTicket("PAJ-17", "Extra-Project", "Adiabatic process")
    JiraTicket.createTicket("PAJ-18", "Extra-Project", "Adiabatic wall")
    JiraTicket.createTicket("PAJ-19", "Extra-Project", "Aerobic digestion")
    JiraTicket.createTicket("PAJ-20", "Extra-Project", "Aerodynamics")
    JiraTicket.createTicket("PAJ-21", "Extra-Project", "Aerospace engineering")
    JiraTicket.createTicket("PAJ-22", "Extra-Project", "Afocal system")
    JiraTicket.createTicket("PAJ-23", "Extra-Project", "Agricultural engineering")
    JiraTicket.createTicket("PAJ-24", "Extra-Project", "Albedo")
    JiraTicket.createTicket("PAJ-25", "Extra-Project", "Alkane")
    JiraTicket.createTicket("PAJ-26", "Extra-Project", "Alkene")
    JiraTicket.createTicket("PAJ-27", "Extra-Project", "Alkyne")
    JiraTicket.createTicket("PAJ-28", "Extra-Project", "Alloy")
    JiraTicket.createTicket("PAJ-29", "Extra-Project", "Alpha particle")
    JiraTicket.createTicket("PAJ-30", "Extra-Project", "Alternating current")
    JiraTicket.createTicket("PAJ-31", "Extra-Project", "Alternative hypothesis")
    JiraTicket.createTicket("PAJ-32", "Extra-Project", "Ammeter")
    JiraTicket.createTicket("PAJ-33", "Extra-Project", "Amino acids")
    JiraTicket.createTicket("PAJ-34", "Extra-Project", "Amorphous solid")
    JiraTicket.createTicket("PAJ-35", "Extra-Project", "Ampere")
    JiraTicket.createTicket("PAJ-36", "Extra-Project", "Amphoterism")
    JiraTicket.createTicket("PAJ-37", "Extra-Project", "Amplifier")
    JiraTicket.createTicket("PAJ-38", "Extra-Project", "Amplitude")
    JiraTicket.createTicket("PAJ-39", "Extra-Project", "Anaerobic digestion")
    JiraTicket.createTicket("PAJ-40", "Extra-Project", "Angular acceleration")
    JiraTicket.createTicket("PAJ-41", "Extra-Project", "Angular momentum")
    JiraTicket.createTicket("PAJ-42", "Extra-Project", "Angular velocity")
    JiraTicket.createTicket("PAJ-43", "Extra-Project", "Anion")
    JiraTicket.createTicket("PAJ-44", "Extra-Project", "Annealing (metallurgy)")
    JiraTicket.createTicket("PAJ-45", "Extra-Project", "Annihilation")
    JiraTicket.createTicket("PAJ-46", "Extra-Project", "Anode")
    JiraTicket.createTicket("PAJ-47", "Extra-Project", "ANSI")
    JiraTicket.createTicket("PAJ-48", "Extra-Project", "Anti-gravity")
    JiraTicket.createTicket("PAJ-49", "Extra-Project", "Applied engineering")
    JiraTicket.createTicket("PAJ-50", "Extra-Project", "Applied mathematics")
    JiraTicket.createTicket("PAJ-51", "Extra-Project", "Arc length")
    JiraTicket.createTicket("PAJ-52", "Extra-Project", "Archimedes' principle")
    JiraTicket.createTicket("PAJ-53", "Extra-Project", "Area moment of inertia")
    JiraTicket.createTicket("PAJ-54", "Extra-Project", "Arithmetic mean")
    JiraTicket.createTicket("PAJ-55", "Extra-Project", "Arithmetic progression")
    JiraTicket.createTicket("PAJ-56", "Extra-Project", "Aromatic hydrocarbon")
    JiraTicket.createTicket("PAJ-57", "Extra-Project", "Arrhenius equation")
    JiraTicket.createTicket("PAJ-58", "Extra-Project", "Artificial intelligence")
    JiraTicket.createTicket("PAJ-59", "Extra-Project", "Assembly language")
    JiraTicket.createTicket("PAJ-60", "Extra-Project", "Atomic orbital")
    JiraTicket.createTicket("PAJ-61", "Extra-Project", "Atomic packing factor")
    JiraTicket.createTicket("PAJ-62", "Extra-Project", "Audio frequency")
    JiraTicket.createTicket("PAJ-63", "Extra-Project", "Austenitization")
    JiraTicket.createTicket("PAJ-64", "Extra-Project", "Automation")
    JiraTicket.createTicket("PAJ-65", "Extra-Project", "Autonomous vehicle")
    JiraTicket.createTicket("PAJ-66", "Extra-Project", "Azimuthal quantum number")

    PersonTickets.assignTickets("PAJ-1", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-1", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-1", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-2", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-2", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-3", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-3", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-3", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-3", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-3", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-4", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-4", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-4", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-5", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-5", "Harvie Betts")
    PersonTickets.assignTickets("PAJ-5", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-6", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-6", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-6", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-6", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-6", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-6", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-6", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-7", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-7", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-7", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-7", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-7", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-7", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-7", "Aasiyah Mata")
    PersonTickets.assignTickets("PAJ-8", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-8", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-8", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-9", "Zain Li")
    PersonTickets.assignTickets("PAJ-9", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-9", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-9", "Zain Li")
    PersonTickets.assignTickets("PAJ-9", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-9", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-10", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-10", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-10", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-10", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-10", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-11", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-11", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-11", "Zain Li")
    PersonTickets.assignTickets("PAJ-11", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-11", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-11", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-12", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-12", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-12", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-13", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-13", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-13", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-14", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-14", "Zain Li")
    PersonTickets.assignTickets("PAJ-14", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-14", "Harvie Betts")
    PersonTickets.assignTickets("PAJ-14", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-14", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-14", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-15", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-15", "Bea Key")
    PersonTickets.assignTickets("PAJ-15", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-15", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-16", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-16", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-16", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-17", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-17", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-17", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-17", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-18", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-18", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-18", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-18", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-18", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-18", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-18", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-19", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-19", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-19", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-19", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-19", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-19", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-20", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-20", "Harvie Betts")
    PersonTickets.assignTickets("PAJ-20", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-20", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-20", "Zain Li")
    PersonTickets.assignTickets("PAJ-20", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-21", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-21", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-21", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-21", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-22", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-22", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-23", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-23", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-23", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-24", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-24", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-24", "Bea Key")
    PersonTickets.assignTickets("PAJ-24", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-24", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-25", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-25", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-25", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-25", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-26", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-26", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-26", "Isla Good")
    PersonTickets.assignTickets("PAJ-27", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-27", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-27", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-27", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-27", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-27", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-28", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-28", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-28", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-28", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-28", "Isla Good")
    PersonTickets.assignTickets("PAJ-28", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-28", "Isla Good")
    PersonTickets.assignTickets("PAJ-29", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-29", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-29", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-29", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-29", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-30", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-30", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-31", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-31", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-31", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-32", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-32", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-32", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-32", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-32", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-32", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-33", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-33", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-33", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-33", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-33", "Bea Key")
    PersonTickets.assignTickets("PAJ-33", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-33", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-34", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-34", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-34", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-34", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-34", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-35", "Aasiyah Mata")
    PersonTickets.assignTickets("PAJ-35", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-35", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-35", "Zain Li")
    PersonTickets.assignTickets("PAJ-35", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-36", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-36", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-36", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-36", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-36", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-37", "Zain Li")
    PersonTickets.assignTickets("PAJ-37", "Aasiyah Mata")
    PersonTickets.assignTickets("PAJ-38", "Aasiyah Mata")
    PersonTickets.assignTickets("PAJ-38", "Aasiyah Mata")
    PersonTickets.assignTickets("PAJ-38", "Harvie Betts")
    PersonTickets.assignTickets("PAJ-38", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-38", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-38", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-39", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-39", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-39", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-39", "Zain Li")
    PersonTickets.assignTickets("PAJ-39", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-39", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-39", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-40", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-40", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-40", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-41", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-41", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-41", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-41", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-41", "Zain Li")
    PersonTickets.assignTickets("PAJ-41", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-41", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-42", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-42", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-42", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-42", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-43", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-43", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-43", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-43", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-43", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-43", "Isla Good")
    PersonTickets.assignTickets("PAJ-44", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-44", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-44", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-44", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-44", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-44", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-44", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-45", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-45", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-45", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-45", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-45", "Zain Li")
    PersonTickets.assignTickets("PAJ-45", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-45", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-46", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-46", "Zain Li")
    PersonTickets.assignTickets("PAJ-46", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-46", "Aasiyah Mata")
    PersonTickets.assignTickets("PAJ-46", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-47", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-47", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-47", "Bea Key")
    PersonTickets.assignTickets("PAJ-47", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-48", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-48", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-48", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-48", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-48", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-48", "Myrtle Schroeder")
    PersonTickets.assignTickets("PAJ-49", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-49", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-49", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-49", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-49", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-49", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-50", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-50", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-50", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-50", "Zain Li")
    PersonTickets.assignTickets("PAJ-50", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-51", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-51", "Asim Hobbs")
    PersonTickets.assignTickets("PAJ-51", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-51", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-51", "Brandi Davey")
    PersonTickets.assignTickets("PAJ-51", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-52", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-52", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-52", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-52", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-52", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-52", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-53", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-53", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-53", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-54", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-54", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-54", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-54", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-54", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-55", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-55", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-55", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-55", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-55", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-55", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-55", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-56", "Isla Good")
    PersonTickets.assignTickets("PAJ-56", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-56", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-56", "Aaron Bryant")
    PersonTickets.assignTickets("PAJ-57", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-57", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-58", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-58", "Rajveer Wright")
    PersonTickets.assignTickets("PAJ-58", "Bea Key")
    PersonTickets.assignTickets("PAJ-58", "Bea Key")
    PersonTickets.assignTickets("PAJ-58", "Ihsan Vu")
    PersonTickets.assignTickets("PAJ-58", "Philippa Rocha")
    PersonTickets.assignTickets("PAJ-58", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-59", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-59", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-59", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-59", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-60", "Meerab Hills")
    PersonTickets.assignTickets("PAJ-60", "Polly Findlay")
    PersonTickets.assignTickets("PAJ-60", "Cassie Mccartney")
    PersonTickets.assignTickets("PAJ-60", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-60", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-61", "Lester Hayward")
    PersonTickets.assignTickets("PAJ-61", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-61", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-62", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-62", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-62", "Ivy Ayala")
    PersonTickets.assignTickets("PAJ-62", "Fred Gallagher")
    PersonTickets.assignTickets("PAJ-62", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-62", "Kaitlyn Pineda")
    PersonTickets.assignTickets("PAJ-62", "Nela Hoffman")
    PersonTickets.assignTickets("PAJ-63", "Isobel Landry")
    PersonTickets.assignTickets("PAJ-63", "Bea Key")
    PersonTickets.assignTickets("PAJ-63", "Sneha Marsh")
    PersonTickets.assignTickets("PAJ-63", "Isla Good")
    PersonTickets.assignTickets("PAJ-63", "Arman Yoder")
    PersonTickets.assignTickets("PAJ-63", "Gracie Byrd")
    PersonTickets.assignTickets("PAJ-63", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-64", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-64", "Ariana Bevan")
    PersonTickets.assignTickets("PAJ-64", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-65", "Harvie Betts")
    PersonTickets.assignTickets("PAJ-65", "Luc Fletcher")
    PersonTickets.assignTickets("PAJ-66", "Sameeha Bowers")
    PersonTickets.assignTickets("PAJ-66", "Isha Wilson")
    PersonTickets.assignTickets("PAJ-66", "Bessie Oakley")
    PersonTickets.assignTickets("PAJ-66", "Harvie Betts")
    PersonTickets.assignTickets("PAJ-66", "Esmai Clark")
    PersonTickets.assignTickets("PAJ-66", "Isha Wilson")
