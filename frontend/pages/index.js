import Head from "next/head";

import Link from "next/link";

export default function Home() {
  return (
    <div>
      <h1 style={{ fontWeight: "bold", fontSize: 50 }}>
        Maximise human hours, minimise humans on site
      </h1>
      <div className="buttons is-centered">
        <Link href="/signup">
          <button className="button is-primary">Sign Up</button>
        </Link>
        <Link href="/login">
          <button className="button">Login</button>
        </Link>
      </div>
    </div>
  );
}
