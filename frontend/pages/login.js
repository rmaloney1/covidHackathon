import Router from "next/router";

import { useToasts } from "react-toast-notifications";

export default function login() {
  const { addToast } = useToasts();

  const handleLogin = () => {
    addToast("logged in!", {
      appearance: "success",
      autoDismiss: true,
      autoDismissTimeout: 2500,
    });
    Router.push("/calendar");
  };

  return (
    <div className="columns is-centered">
      <div className="column is-4 box">
        <h1 className="title is-3">Log In</h1>
        <div className="field">
          <label className="label">Email</label>
          <input className="input" type="email" />
        </div>
        <div className="field">
          <label className="label">Password</label>
          <input className="input" type="password" />
        </div>
        <button
          className="button is-light is-success"
          onClick={() => handleLogin()}
        >
          Login
        </button>
      </div>
    </div>
  );
}
