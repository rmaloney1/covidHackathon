import Task from "../components/Task/Task";

import { useState } from "react";

import { useToasts } from "react-toast-notifications";

export default function Tasks() {
  const [tasks, updateTasks] = useState([
    { name: "task1", status: "none", attendees: ["Tom Hill", "Tom Wright"] },
    { name: "yeet", status: "none", attendees: ["Tom Hill", "Tom Wright"] },
  ]);

  const [search, setSearch] = useState("");

  const { addToast } = useToasts();

  const handleRemoteClick = (task) => {
    addToast(`Doing ${task.name} remotely`, {
      appearance: "success",
      autoDismiss: true,
      autoDismissTimeout: 2500,
    });
  };

  const handleInPersonClick = (task) => {
    addToast(`Doing ${task.name} in person`, {
      appearance: "success",
      autoDismiss: true,
      autoDismissTimeout: 2500,
    });
  };

  return (
    <div>
      <div className="columns">
        <div className="column is-4">
          <h1 className="title is-2">Tasks from Jira</h1>
        </div>
        <div className="column is-8">
          <input
            className="input is-rounded"
            type="text"
            placeholder="search"
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>
      <div className="columns is-multiline">
        {tasks
          .filter((t) => t.name.toLowerCase().includes(search.toLowerCase()))
          .map((task, idx) => (
            <div key={idx} className="column is-3">
              <Task
                key={idx}
                task={task}
                onRemote={handleRemoteClick}
                onInPerson={handleInPersonClick}
              />
            </div>
          ))}
      </div>
    </div>
  );
}
