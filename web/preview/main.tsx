import React from "react";
import ReactDOM from "react-dom/client";
import App from "../src/App";
import "../src/styles.css";
import "../src/features.css";

/** Preview harness: ?view=login | ops | ops-hold | ops-drag | ops-medal | party | driver | depot | merchant | rewards.
 *  "./lib" is swapped for mock-lib.ts by the vite alias. */
const view = new URLSearchParams(window.location.search).get("view") ?? "ops";
const INITIAL_CASE: Record<string, string> = {
  ops: "D103", "ops-drag": "D103", "ops-medal": "D103", "ops-hold": "D104", party: "D103", driver: "D105", depot: "D107", merchant: "D106",
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App initialCase={INITIAL_CASE[view]} initialPage={view === "rewards" ? "rewards" : "desk"} />
  </React.StrictMode>,
);

/* Scripted interactions for the screenshot states. */
if (view === "ops-medal") {
  // Approve the top draft with the keyboard: shows the coin toast and the first medal unlock.
  setTimeout(() => window.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true })), 3300);
}
if (view === "ops-drag") {
  // Drag the top card 90px to the right and hold it there: shows the tilt, the "Approve" word and the peeking cards.
  setTimeout(() => {
    const card = document.querySelector(".deck__card--top .headline-md") as HTMLElement | null;
    if (!card) return;
    const r = card.getBoundingClientRect();
    const x = r.left + 40, y = r.top + 10;
    const opts = (cx: number) => ({ clientX: cx, clientY: y, pointerId: 1, button: 0, bubbles: true, isPrimary: true });
    card.dispatchEvent(new PointerEvent("pointerdown", opts(x)));
    for (let i = 1; i <= 9; i++) card.dispatchEvent(new PointerEvent("pointermove", opts(x + i * 10)));
  }, 1500);
}
