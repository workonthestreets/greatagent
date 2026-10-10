import React from "react";
import ReactDOM from "react-dom/client";
import App from "../src/App";
import "../src/styles.css";

/** Preview harness: ?view=login | ops | ops-hold | party. "./lib" is swapped for mock-lib.ts by the vite alias. */
const view = new URLSearchParams(window.location.search).get("view") ?? "ops";
const initialCase = view === "ops" ? "D103" : view === "ops-hold" ? "D104" : view === "party" ? "D103" : undefined;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App initialCase={initialCase} />
  </React.StrictMode>,
);
