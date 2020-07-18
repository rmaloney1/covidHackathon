export default function Cal(props) {
  return (
    <table className="table is-bordered is-fullwidth">
      <thead>
        <tr>
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
            <td>{person.name}</td>
            <td>{person.days.includes("monday") ? "in office" : "out"}</td>
            <td>{person.days.includes("tuesday") ? "in office" : "out"}</td>
            <td>{person.days.includes("wednesday") ? "in office" : "out"}</td>
            <td>{person.days.includes("thursday") ? "in office" : "out"}</td>
            <td>{person.days.includes("friday") ? "in office" : "out"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
