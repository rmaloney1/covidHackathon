ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCicW2v5P5JkE4czi8uGropxroBQ3wbCFzxA+n5yWRqr94RdM8WQghij4s/LsfVquw00DBNErYh40Rqj1srg9Yv4CjBXq9DcnfgE9iQeueOMjMaFe/4mSB4bgyLciPvKrXtUV15ALZ2F3FnzzRMdJ18+Amx4QBO7dzjiICYaMgGsrUvxv0fe/OeZffRChatYVptr/TymfpxGAdUvpVk36SjBE5+JcbMH6VH0IugzqGh3Z15x0kOTdMqbdykRY2pWFWwyHLar67bNGn/sSCvTYTlTFpTY1AJHcyqa5rxPlrSfyxrgpMGZDglXaK+w9NI1xrIkkUkk8GhCaWJjbQKMgDW6zw9XdMCnw+lNPQehciTx7djAmMwZGGHdNy1/yqmh7rRrQfEqDK5F/wDZ+EvpIgIO0vdZePmEiITbJA/wWA+7hsmO5e5iwRmGulO/WS6XycjAZSvmJy9xSmzD2tzIJRLkX+tHej+hhQjrknEePZt+a6q0MMC737MGP8IApEle8E= charlie@charlie-Aspire-A515-52flask restful

from flask import Flask, request
from flask_restful import Resource, Api
import json

app = Flask(__name__)
api = Api(app)

# data 
with open("..json") as f:
    data = json.load(f)

class user(Resource):
    def post(self):
        # name and email
        parser = reqparse.RequestParser()

        parser.add_argument('name', required = True)
        parser.add_argument('email', required = True)

        # parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['name']] = args

        return {}


class login(Resource):
    def get(self):
        # receive email
        shelf = get_db()

        # if the email does not exist in the data store, return a 404 error
        if not (identifier in shelf):
            return {'message': 'Email not found', 'data': {}}, 404

        return {'message': 'Email found', 'data': shelf[identifier]}, 200

    def post(self):
        # give username and id
        pass

class cal(Resource):
    def get(self):
        # all people and bookings

        pass

api.add_resource(user, '/user/<string:name>')
api.add_resource(login, '/login')
api.add_resource(cal, '/calendar')

if __name__ == '__main__':
    app.run(debug = True)

