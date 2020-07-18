export default function admin() {
  const handleEdit = () => {};
  return (
    <div className="columns is-centered">
      <div className="column is-4 box">
        <h1 className="title is-3">Office Admin</h1>
        <div className="field">
          <label className="label">Capacity</label>
          <input className="input" type="text" placeholder="42069" />
        </div>

        <button className="button is-light is-success" onClick={handleEdit}>
          Edit
        </button>
      </div>
    </div>
  );
}
