export default function signup() {
  const handleSignUp = () => {
    console.log("dosignup");
  };

  return (
    <div className="columns is-centered">
      <div className="column is-4 box">
        <h1 className="title is-3">Sign Up</h1>
        <div className="field">
          <label className="label">Name</label>
          <input className="input" type="text" placeholder="Jon Snow" />
        </div>
        <div className="field">
          <label className="label">Email</label>
          <input
            className="input"
            type="email"
            placeholder="jon@winterfell.westeros"
          />
        </div>
        <div className="field">
          <label className="label">Password</label>
          <input className="input" type="password" />
        </div>
        <button className="button is-light is-success" onClick={handleSignUp}>
          Signup
        </button>
      </div>
    </div>
  );
}
