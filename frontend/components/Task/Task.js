import { useState } from "react";

import DatePicker from "react-datepicker";

export default function Task(props) {
  const [showModal, setShowModal] = useState(false);
  const [endDate, setEndDate] = useState(null);
  const [startDate, setStartDate] = useState(new Date());

  const onChange = (dates) => {
    const [start, end] = dates;
    setStartDate(start);
    setEndDate(end);
  };

  const handleInPerson = () => {
    setShowModal(true);
    // props.onInPerson(props.task);
  };

  return (
    <>
      <div className="box has-text-centered">
        <h3 className="is-size-4">{props.task.name}</h3>
        <p className="tags is-centered">
          {props.task.attendees.map((a, idx) => (
            <span className="tag is-dark" key={idx}>
              {a}
            </span>
          ))}
        </p>

        <div className="buttons is-centered">
          {/* <button
            className="button is-light is-info is-small"
            onClick={() => props.onRemote(props.task)}
          >
            Do online
          </button> */}
          <button
            className="button is-light is-primary"
            onClick={() => handleInPerson()}
          >
            Do in person
          </button>
        </div>
      </div>

      {showModal ? (
        <div className="modal is-active">
          <div
            className="modal-background"
            onClick={() => setShowModal(false)}
          ></div>
          <div className="modal-content">
            <div className="box has-text-centered">
              <p>
                <strong>Meeting must be between:</strong>
              </p>
              <DatePicker
                selected={startDate}
                onChange={onChange}
                startDate={startDate}
                endDate={endDate}
                selectsRange
                inline
              />
              <p>
                <strong>Priority:</strong>
              </p>
              <div className="field">
                <div className="select">
                  <select>
                    <option>High</option>
                    <option>Low</option>
                  </select>
                </div>
              </div>
              <div className="buttons">
                <button
                  className="button is-success"
                  onClick={() => {
                    setShowModal(false);
                    props.onInPerson({
                      ...props.task,
                      afterDate: startDate,
                      endDate,
                      meeting: true,
                      priority: "high",
                    });
                  }}
                >
                  Submit
                </button>
                <button
                  className="button is-danger is-light"
                  onClick={() => setShowModal(false)}
                >
                  Discard
                </button>
              </div>
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
