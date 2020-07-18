import Cal from "../components/Cal/Cal";

import { useContext } from "react";
import UserContext from "../context/auth";

export default function Calendar() {
  // const [user, setUser] = useContext(UserContext);
  const user = { name: "Tom Hill" };

  const peeps = [
    { name: "Tom Shortay", days: ["monday", "tuesday", "wednesday"] },
    { name: "Rohan Maloney", days: ["monday", "tuesday", "wednesday"] },
    { name: "Charlie Wyatt", days: ["monday", "thursday", "wednesday"] },
    { name: "Tom Wright", days: ["monday", "friday", "tuesday"] },
  ];

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
    </>
  );
}
