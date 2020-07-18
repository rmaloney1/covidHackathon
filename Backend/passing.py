from flask import Flask, request
from flask_restful import Resource, Api, abort
import json
from models import CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest, model_to_dict



app = Flask(__name__)
api = Api(app)

# data 
# with open("..json") as f:
#     data = json.load(f)

class user(Resource):
    def post(self):
        # name and email
        data = json.loads(request.json)
        name = data["name"]
        email = data["email"]
        Person.createPerson(name, email)
        return {}

    def get(self):
        email = request.args["email"]
        person = Person.select().where(Person.email==email).get()
        if not person:
            return abort(404)

        return {person.personID, email}
        


class tasks(Resource):
    def get(self):
        
        tasks = JiraTicket.select()
        verbose = []
        for task in tasks:
            details = {}
            details["name"] = task.name
            details["status"] = "in person" if task.assigned else "unassigned"
            attendees = PersonTickets.select().where(PersonTickets.ticketID==task.ticketID)
            names = [i.person.personID for i in attendees]
            details["attendees"] = names
            verbose.append(details)

        return verbose

class calendar(Resource):
    def get(self):
        # all people and bookings

        pass

api.add_resource(user, '/user')
api.add_resource(tasks, '/tasks')
api.add_resource(calendar, '/calendar')

if __name__ == '__main__':
    app.run(debug = True)

