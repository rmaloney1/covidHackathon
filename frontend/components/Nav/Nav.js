import Link from "next/link";

import { nav } from "./Nav.module.scss";

import { useEffect, useContext } from "react";
import UserContext from "../../context/auth";

export default function Nav() {
  // const [user, setUser] = useContext(UserContext);

  const user = { name: "Tom Hill" };

  // const user = { name: "Tom Hill", id: 1 };
  // useEffect(() => {
  //   setUser({ name: "Tom Hill", id: 1 });
  // }, []);

  return (
    <>
      <nav className={`${nav} navbar is-fixed-top`}>
        <div className="navbar-brand">
          <div className="navbar-item">
            <Link href={user ? "/calendar" : "/"}>
              <h1 className="title is-2">COVIDSpace</h1>
            </Link>
          </div>

          <a
            role="button"
            className="navbar-burger burger"
            aria-label="menu"
            aria-expanded="false"
            data-target="navbarBasicExample"
          >
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>
        <div className="navbar-menu">
          <div className="navbar-end">
            {!user ? (
              <div className="navbar-item">
                <div className="buttons">
                  <a className="button is-primary">
                    <Link href="/signup">
                      <strong>Sign up</strong>
                    </Link>
                  </a>
                  <a className="button is-l9ight">
                    <Link href="/signup">Log in</Link>
                  </a>
                </div>
              </div>
            ) : (
              <div className="navbar-item">
                <div className="buttons">
                  <a className="button is-primary">
                    <Link href="/tasks">
                      <strong>Manage Task Meetings</strong>
                    </Link>
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>
      <div style={{ height: "5rem" }}></div>
    </>
  );
}
