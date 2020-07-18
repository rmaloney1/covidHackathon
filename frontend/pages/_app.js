import "../styles/styles.scss";
import "react-datepicker/dist/react-datepicker.css";

import { ToastProvider } from "react-toast-notifications";

import Nav from "../components/Nav/Nav";

import UserContext from "../context/auth";

function CovidSpace({ Component, pageProps }) {
  return (
    <UserContext.Provider value={{ name: "Tom Hill", id: 1 }}>
      <ToastProvider>
        <Nav />
        <div className="container">
          <Component {...pageProps} />
        </div>
      </ToastProvider>
    </UserContext.Provider>
  );
}

export default CovidSpace;
