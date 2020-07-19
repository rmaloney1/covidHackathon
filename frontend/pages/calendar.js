import Cal from "../components/Cal/Cal";

import { useContext, useState, useEffect } from "react";
import { useToasts } from "react-toast-notifications";
import UserContext from "../context/auth";
import API from "../lib/api/api";

export default function Calendar() {
  // const [user, setUser] = useContext(UserContext);
  const user = { name: "Tom Hill" };

  // const peeps = [
  //   { name: "Tom Shortay", days: ["monday", "tuesday", "wednesday"] },
  //   { name: "Rohan Maloney", days: ["monday", "tuesday", "wednesday"] },
  //   { name: "Charlie Wyatt", days: ["monday", "thursday", "wednesday"] },
  //   { name: "Tom Wright", days: ["monday", "friday", "tuesday"] },
  // ];

  const peepsStart = [
    {
      name: "Tom Shortay",
      meetings: [
        { name: "task 1", day: "thursday" },
        { name: "task 4", day: "thursday" },
        { name: "task 2", day: "monday" },
      ],
    },
    {
      name: "Rohan Maloney",
      meetings: [
        { name: "task 1", day: "thursday" },
        { name: "task 4", day: "thursday" },
        { name: "task 2", day: "monday" },
      ],
    },
    {
      name: "Charlie Wyatt",
      meetings: [
        { name: "task 1", day: "monday" },
        { name: "task 4", day: "wednesday" },
        { name: "task 2", day: "friday" },
      ],
    },
    {
      name: "Tom Wright",
      meetings: [
        { name: "task 5", day: "tuesday" },
        { name: "task 4", day: "tuesday" },
        { name: "task 2", day: "tuesday" },
      ],
    },
  ];

  const [peeps, setPeeps] = useState(peepsStart);

  const { addToast } = useToasts();

  useEffect(() => {
    API.getCalendar()
      .then((res) => {
        console.log(res);
        const data = res.data;
        data.forEach((p) => {
          if (!p.meetings) {
            p.meetings = [];
          }
        });
        console.log(data);
        setPeeps(data);
      })
      .catch((err) => {
        console.error(err);
      });
  }, []);

  const handleAllocate = () => {
    API.allocate().then((res) => {
      console.log(res);
      addToast("Allocated tasks", {
        appearance: "success",
        autoDismiss: true,
        autoDismissTimeout: 2500,
      });
    });
  };

  return (
    <>
      <h3 className="title is-4">
        Hi there, {user ? user.name.split(" ")[0] : "Not logged in!"}.
        <br />
        <br />
        Find a spot at the office.
      </h3>
      <div className="columns is-centered">
        <div className="column is-10 box">
          <Cal people={peeps} />
        </div>
      </div>
      <center>
        <button
          className="button is-light is-warning has-text-centered"
          onClick={() => handleAllocate()}
        >
          For Demo: Allocate Meetings
        </button>
      </center>
      <br />
      <br />
      <br />
    </>
  );
}
