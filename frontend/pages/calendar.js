import Cal from "../components/Cal/Cal";

export default function Calendar() {
  const peeps = [
    { name: "Tom Shortay", days: ["monday", "tuesday", "wednesday"] },
    { name: "Rohan Maloney", days: ["monday", "tuesday", "wednesday"] },
    { name: "Charlie Wyatt", days: ["monday", "thursday", "wednesday"] },
    { name: "Tom Wright", days: ["monday", "friday", "tuesday"] },
  ];

  return (
    <div className="columns is-centered">
      <div className="column is-10 box">
        <Cal people={peeps} />
      </div>
    </div>
  );
}
