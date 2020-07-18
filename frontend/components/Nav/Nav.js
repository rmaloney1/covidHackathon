import Link from "next/link";

import { nav } from "./Nav.module.scss";

export default function Nav() {
  const user = false;

  return (
    <>
      <nav className={`${nav} navbar is-fixed-top`}>
        <div className="navbar-brand">
          <div className="navbar-item">
            <Link href="/">
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
            {user ? (
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
