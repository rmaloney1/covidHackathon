from flask import Flask, request
from flask_restful import Resource, Api, abort
import json
import datetime as dt
from models import (
    CompanyBuildings,
    Person,
    Project,
    JiraTicket,
    PersonTickets,
    MeetingRequest,
    model_to_dict,
    apiUser,
    ourProject,
)
from processing import contactTrace, makeAllocations

me = apiUser("rohanmaloney@outlook.com", "lxZVdyemldyTFkmwM5Hn94BD")
auth = me.getAuth()

app = Flask(__name__)
api = Api(app)

# data
# with open("..json") as f:
#     data = json.load(f)


class user(Resource):
    def post(self):
        # name and email
        data = request.json
        name = data["name"]
        email = data["email"]
        Person.createPerson(name, email)
        return {}

    def get(self):
        print("hi")
        email = request.args["email"]
        try:
            person = Person.select().where(Person.email == email).get()
        except:
            return abort(404)

        return {"name": person.personID, "email": email}


class tasks(Resource):
    def get(self):
        print("yo")
        tasks = JiraTicket.select()
        verbose = []
        for task in tasks:
            details = {}
            details["id"] = task.ticketID
            details["name"] = task.name
            print("name of", task.ticketID, "is", task.name)
            details["status"] = "in person" if task.assigned else "unassigned"
            attendees = PersonTickets.select().where(
                PersonTickets.ticketID == task.ticketID
            )
            names = [i.person.personID for i in attendees]
            details["attendees"] = names
            verbose.append(details)

        return verbose

    def post(self):
        # name and email
        data = request.json
        # print(f"DATAAAAAAAAAAAAAAAAAAAAAAAAAAA {data}")
        ticketID = data["ticketID"]
        afterDate = dt.datetime.strptime(
            data["afterDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ).date()
        dueDate = dt.datetime.strptime(data["dueDate"], "%Y-%m-%dT%H:%M:%S.%fZ").date()
        print(afterDate)
        print(type(afterDate))
        priority = data["priority"]
        if priority == "high":
            priority = True
        else:
            priority = False

        MeetingRequest.makeRequest(ticketID, afterDate, dueDate, priority)
        return {}


class refresh(Resource):
    def post(self):
        ourProject.refreshTickets(auth)
        return {}


class calendar(Resource):
    def get(self):
        output = []
        # A list of all people that have a allocated task
        # fullPersonTaskList = (
        #     PersonTickets.select()
        #     .join(
        #         MeetingRequest, on=(MeetingRequest.ticketID == PersonTickets.ticketID)
        #     )
        #     .where(MeetingRequest.requestFilled == True)
        # )
        all_people = Person.select()
        for person in all_people.iterator():
            allocated_tickets = (
                JiraTicket.select()
                .join(PersonTickets, on=(JiraTicket.ticketID == PersonTickets.ticketID))
                .join(
                    MeetingRequest, on=(MeetingRequest.ticketID == JiraTicket.ticketID)
                )
                .where(
                    (MeetingRequest.requestFilled == True)
                    & (PersonTickets.person == person.personID)
                )
            )
            print(list(allocated_tickets))
            mytasks = []

            weekDays = (
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            )

            for ticket in allocated_tickets:
                print(type(ticket))
                # print(
                #     MeetingRequest.select()
                #             .where(MeetingRequest.ticketID == ticket.ticketID)
                #             .get()
                #             .dateAllocated
                #         ).strftime("%m/%d/%Y")
                #         )
                mytasks.append(
                    {
                        "name": ticket.name,
                        # "day": (ticket.switch(MeetingRequest).dateAllocated).strftime(
                        #     "%m/%d/%Y"
                        # ),
                        "day": weekDays[
                            (
                                MeetingRequest.select()
                                .where(MeetingRequest.ticketID == ticket.ticketID)
                                .get()
                                .dateAllocated
                            ).weekday()
                        ],
                        "attendees": [
                            t.person.personID
                            for t in PersonTickets.select().where(
                                PersonTickets.ticketID == ticket.ticketID
                            )
                        ],
                    }
                )
            output.append({"name": person.personID, "meetings": mytasks})
        # for personTask in fullPersonTaskList.iterator():
        #     found = False
        #     taskSummary = {
        #         "name": personTask.ticketID.name,
        #         "attendees": [
        #             t
        #             for t in PersonTickets.select().where(
        #                 PersonTickets.person == personTask.person
        #             )
        #         ],
        #         "day": (personTask.dateAllocated).strftime("%m/%d/%Y"),
        #     }
        #     for i in output:
        #         if output[i]["Name"] == personTask.person:
        #             found = True
        #             output[i]["meetings"].append(taskSummary)

        #     if not found:
        #         output.append({"Name": personTask.person, "meetings": [taskSummary]})
        return output


class trace(Resource):
    def get(self, p_id):
        return contactTrace(p_id)


class allocate(Resource):
    def post(self):
        makeAllocations()
        return {}


api.add_resource(user, "/user")
api.add_resource(tasks, "/tasks")
api.add_resource(calendar, "/calendar")
api.add_resource(trace, "/trace/<string:p_id>")
api.add_resource(allocate, "/allocate")
api.add_resource(refresh, "/refresh")

if __name__ == "__main__":
    app.run(debug=True)
