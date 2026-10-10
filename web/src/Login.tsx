import { useState } from "react";
import { DEMO_PASSWORD, supabase } from "./lib";
import { Mark, Phone, User } from "./icons";

const OTHER_DEMO = ["admin", "driver", "depot", "merchant"];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");   // the demo email being signed in, or "form"

  const signIn = async (e?: React.FormEvent, demoEmail?: string) => {
    e?.preventDefault();
    if (busy) return;
    setError("");
    setBusy(demoEmail ?? "form");
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: demoEmail ?? email,
        password: demoEmail ? DEMO_PASSWORD : password,
      });
      if (error) setError(`${demoEmail ? `Could not sign in as ${demoEmail.split("@")[0]}: ` : ""}${error.message}`);
    } finally {
      setBusy("");
    }
  };

  return (
    <div className="page framed app login">
      <nav className="nav">
        <span />
        <span className="nav__mark" aria-label="Rivet Delivery Desk" role="img"><Mark /></span>
        <span />
      </nav>

      <section className="hero column center">
        <h1 className="display-lg">The delivery desk that knows when to <span className="emphasis">wait</span>.</h1>
        <p className="hero__sub body-lg text-muted">
          Rivet's agent decides the next safe step on every delivery case, and hands over to a person when it cannot.
        </p>
      </section>

      <form onSubmit={signIn} className="card login__form">
        <label className="field">
          <span className="field__label">Email</span>
          <input className="input" type="email" placeholder="you@company.com" value={email}
            onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
        </label>
        <label className="field">
          <span className="field__label">Password</span>
          <input className="input" type="password" value={password}
            onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
        </label>
        {error && <p className="error-text" role="alert">{error}</p>}
        <div className="login__actions">
          <button type="submit" className="btn btn--primary" disabled={!!busy}>{busy === "form" ? "Signing in…" : "Sign in"}</button>
          <button type="button" className="btn btn--secondary" onClick={() =>
            supabase.auth.signInWithOAuth({ provider: "google", options: { redirectTo: window.location.origin } })}>
            Continue with Google
          </button>
        </div>
      </form>

      <section className="band-block">
        <div className="spectrum-band band--login" aria-hidden="true" />
        <div className="spectrum-cards">
          <article className="card-feature">
            <span className="card-feature__icon"><User /></span>
            <h2 className="headline-md">Open the desk</h2>
            <p className="card-feature__body">
              Approve the agent's drafts before they go out and watch its live log as it works a case.
            </p>
            <button className="btn btn--inverse card-feature__cta" disabled={!!busy} onClick={() => signIn(undefined, "coordinator@greatagent.demo")}>
              {busy === "coordinator@greatagent.demo" ? "Signing in…" : "Sign in as coordinator"}
            </button>
          </article>
          <article className="card-feature">
            <span className="card-feature__icon"><Phone /></span>
            <h2 className="headline-md">Open the customer portal</h2>
            <p className="card-feature__body">
              Follow one parcel's thread with the desk, the same answers the voice line reads out.
            </p>
            <button className="btn btn--inverse card-feature__cta" disabled={!!busy} onClick={() => signIn(undefined, "customer@greatagent.demo")}>
              {busy === "customer@greatagent.demo" ? "Signing in…" : "Sign in as customer"}
            </button>
          </article>
        </div>
      </section>

      <section className="demo-row">
        <span className="label text-muted">Other demo accounts</span>
        <div className="demo-row__pills">
          {OTHER_DEMO.map((r) => (
            <button key={r} className="btn btn--secondary btn--sm" disabled={!!busy} onClick={() => signIn(undefined, `${r}@greatagent.demo`)}>
              {busy === `${r}@greatagent.demo` ? "Signing in…" : r.charAt(0).toUpperCase() + r.slice(1)}
            </button>
          ))}
        </div>
        {error && busy === "" && <p className="error-text demo-row__error" role="alert">{error}</p>}
      </section>
    </div>
  );
}
