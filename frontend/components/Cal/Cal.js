import faker from "faker";

import { bar } from "./Cal.module.scss";

import { useState } from "react";

function Bar(props) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className={bar} onClick={() => setShowModal(true)}>
        {props.tasks.length} meetings
      </div>
      {showModal ? (
        <div className="modal is-active">
          <div
            className="modal-background"
            onClick={() => setShowModal(false)}
          ></div>
          <div className="modal-content">
            <div className="box has-text-centered">
              <h3 className="title is-3">
                {props.tasks.length} meetings on [DATE]
              </h3>
            </div>
          </div>
          <button
            className="modal-close is-large"
            aria-label="close"
            onClick={() => setShowModal(false)}
          ></button>
        </div>
      ) : null}
    </>
  );
}

export default function Cal(props) {
  return (
    <table className="table  is-fullwidth" style={{ tableLayout: "fixed" }}>
      <thead>
        <tr style={{ textAlign: "center" }}>
          <th>Name</th>
          <th>Monday</th>
          <th>Tuesday</th>
          <th>Wednesday</th>
          <th>Thursday</th>
          <th>Friday</th>
        </tr>
      </thead>
      <tbody>
        {props.people.map((person, idx) => (
          <tr key={idx}>
            <td style={{ textAlign: "center" }}>
              <img
                style={{ borderRadius: 100, height: "32px" }}
                src={faker.image.avatar()}
              />
              <p>{person.name}</p>
            </td>
            <td>
              {person.days.includes("monday") ? <Bar tasks={[]} /> : null}
            </td>
            <td>
              {person.days.includes("tuesday") ? <Bar tasks={[]} /> : null}
            </td>
            <td>
              {person.days.includes("wednesday") ? <Bar tasks={[]} /> : null}
            </td>
            <td>
              {person.days.includes("thursday") ? <Bar tasks={[]} /> : null}
            </td>
            <td>
              {person.days.includes("friday") ? <Bar tasks={[]} /> : null}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
