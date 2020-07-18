import "../styles/styles.scss";

import Nav from "../components/Nav/Nav";

function CovidSpace({ Component, pageProps }) {
  return (
    <>
      <Nav />
      <Component {...pageProps} />
    </>
  );
}

export default CovidSpace;
