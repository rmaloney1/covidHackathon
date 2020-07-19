import { useState } from "react";

import { useToasts } from "react-toast-notifications";

import Router from "next/router";

import API from "../lib/api/api";

export default function signup() {
  const { addToast } = useToasts();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignUp = () => {
    API.register(name, email)
      .then((res) => {
        addToast("Signed up", {
          appearance: "success",
          autoDismiss: true,
          autoDismissTimeout: 2500,
        });

        Router.push("/calendar");
      })
      .catch((err) => {
        console.error(err);
        addToast("Sign up failed: ", {
          appearance: "error",
          autoDismiss: true,
          autoDismissTimeout: 2500,
        });
      });
  };

  return (
    <div className="columns is-centered">
      <div className="column is-4 box">
        <h1 className="title is-3">Sign Up</h1>
        <div className="field">
          <label className="label">Name</label>
          <input
            className="input"
            type="text"
            placeholder="Jon Snow"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className="field">
          <label className="label">Email</label>
          <input
            className="input"
            type="email"
            placeholder="jon@winterfell.westeros"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="field">
          <label className="label">Password</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="button is-light is-success" onClick={handleSignUp}>
          Signup
        </button>
      </div>
    </div>
  );
}
