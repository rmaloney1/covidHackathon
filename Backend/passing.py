ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCicW2v5P5JkE4czi8uGropxroBQ3wbCFzxA+n5yWRqr94RdM8WQghij4s/LsfVquw00DBNErYh40Rqj1srg9Yv4CjBXq9DcnfgE9iQeueOMjMaFe/4mSB4bgyLciPvKrXtUV15ALZ2F3FnzzRMdJ18+Amx4QBO7dzjiICYaMgGsrUvxv0fe/OeZffRChatYVptr/TymfpxGAdUvpVk36SjBE5+JcbMH6VH0IugzqGh3Z15x0kOTdMqbdykRY2pWFWwyHLar67bNGn/sSCvTYTlTFpTY1AJHcyqa5rxPlrSfyxrgpMGZDglXaK+w9NI1xrIkkUkk8GhCaWJjbQKMgDW6zw9XdMCnw+lNPQehciTx7djAmMwZGGHdNy1/yqmh7rRrQfEqDK5F/wDZ+EvpIgIO0vdZePmEiITbJA/wWA+7hsmO5e5iwRmGulO/WS6XycjAZSvmJy9xSmzD2tzIJRLkX+tHej+hhQjrknEePZt+a6q0MMC737MGP8IApEle8E= charlie@charlie-Aspire-A515-52flask restful

from flask import Flask, request
from flask_restful import Resource, Api, abort
import json
from models import CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest, model_to_dict



app = Flask(__name__)
api = Api(app)

# data 
with open("..json") as f:
    data = json.load(f)

class user(Resource):
    def post(self):
        # name and email
        data = json.loads(requests.json)
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

api.add_resource(user, '/user)
api.add_resource(tasks, '/tasks')
api.add_resource(calendar, '/calendar')

if __name__ == '__main__':
    app.run(debug = True)

