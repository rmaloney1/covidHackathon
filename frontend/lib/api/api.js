import axios from "axios";

const SERVER_URL = "http://127.0.0.1:5000";

let api = axios.create({
  baseURL: SERVER_URL,
  header: {
    "content-type": "application/json",
  },
});

const API = {
  login: (email) => api.get(`/user?email=${email}`),
  register: (name, email) => api.post("/user", { name, email }),
  getTasks: () => api.get("/tasks"),
  doTaskInPerson: (id, afterDate, dueDate, priority) =>
    api.post(`/tasks`, { ticketID: id, afterDate, dueDate, priority }),
};

export default API;
