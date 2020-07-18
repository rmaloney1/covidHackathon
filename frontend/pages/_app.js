import "../styles/styles.scss";

import Nav from "../components/Nav/Nav";

function CovidSpace({ Component, pageProps }) {
  return (
    <>
      <Nav />
      <div className="container">
        <Component {...pageProps} />
      </div>
    </>
  );
}

export default CovidSpace;
