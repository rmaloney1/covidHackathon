from flask import Flask, request
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)

todos = {}

class TodoSimple(Resource):
    def get(self, todo_id):
        try:
            todo = todos[todo_id]
            return {todo_id: todo}
        except:
            return abort(404, message="The todo does not exist")

    def put(self, todo_id):
        print("got here")
        print(request.json)
        todos[todo_id] = request.json
        print(todos)
        return {todo_id: todos[todo_id]}

api.add_resource(TodoSimple, '/<string:todo_id>')

if __name__ == '__main__':
    app.run(debug=True)
