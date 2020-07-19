import Task from "../components/Task/Task";

import { useState, useEffect } from "react";

import { useToasts } from "react-toast-notifications";

import API from "../lib/api/api";

export default function Tasks() {
  const [loading, setLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [tasks, updateTasks] = useState([
    { name: "task1", status: "none", attendees: ["Tom Hill", "Tom Wright"] },
    { name: "yeet", status: "none", attendees: ["Tom Hill", "Tom Wright"] },
  ]);

  useEffect(() => {
    setLoading(true);
    API.getTasks()
      .then((res) => {
        console.log(res);
        updateTasks(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const [search, setSearch] = useState("");

  const { addToast } = useToasts();

  const handleRemoteClick = (task) => {
    // never used atm
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    API.refreshJira()
      .then((res) => {
        console.log(res);
        setIsRefreshing(false);
      })
      .catch((err) => {
        console.error(err);
        setIsRefreshing(false);
      });
  };

  const handleInPersonClick = (task) => {
    API.doTaskInPerson(task.id, task.afterDate, task.endDate, task.priority)
      .then((res) => {
        console.log(res);
        addToast(`Doing ${task.name} remotely`, {
          appearance: "success",
          autoDismiss: true,
          autoDismissTimeout: 2500,
        });
      })
      .catch((err) => {
        addToast(`Some error occured`, {
          appearance: "error",
          autoDismiss: true,
          autoDismissTimeout: 2500,
        });
      });
  };

  if (loading) {
    return <div> Fetching tasks from Jira ... </div>;
  }

  return (
    <div>
      <div className="columns">
        <div className="column is-4">
          <h1 className="title is-2"> Tasks from Jira </h1>{" "}
        </div>{" "}
        <div className="column is-8">
          <input
            className="input is-rounded"
            type="text"
            placeholder="search"
            onChange={(e) => setSearch(e.target.value)}
          />{" "}
        </div>{" "}
      </div>{" "}
      <div className="columns is-multiline">
        {" "}
        {tasks
          .filter((t) => t.name.toLowerCase().includes(search.toLowerCase()))
          .map((task, idx) => (
            <div key={idx} className="column is-3">
              <Task
                key={idx}
                task={task}
                onRemote={handleRemoteClick}
                onInPerson={handleInPersonClick}
              />{" "}
            </div>
          ))}{" "}
      </div>{" "}
      <center>
        <button
          className={`button is-light is-warning ${
            isRefreshing ? "is-loading" : null
          }`}
          onClick={() => handleRefresh()}
        >
          For Demo: refresh jira
        </button>
      </center>
    </div>
  );
}
