import Link from "next/link";

import { nav } from "./Nav.module.scss";

export default function Nav() {
  return (
    <nav className={`${nav} navbar`}>
      <div className="navbar-brand">
        <Link className="navbar-item" href="/">
          <h1 className="title is-2">COVIDSpace</h1>
        </Link>

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
    </nav>
  );
}
