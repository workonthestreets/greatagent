import { useState } from "react";
import { supabase } from "./lib";

const DEMO = ["admin", "coordinator", "customer", "driver", "depot", "merchant"];

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const signIn = async (e?: React.FormEvent, demoEmail?: string) => {
    e?.preventDefault();
    setError("");
    const { error } = await supabase.auth.signInWithPassword({
      email: demoEmail ?? email,
      password: demoEmail ? (import.meta.env.VITE_DEMO_PASSWORD || "greatagent-demo") : password,
    });
    if (error) setError(error.message);
  };

  return (
    <div className="login">
      <h1>Rivet Delivery Desk</h1>
      <p className="muted">Sign in to see your deliveries and cases.</p>
      <button className="primary wide" onClick={() =>
        supabase.auth.signInWithOAuth({ provider: "google", options: { redirectTo: window.location.origin } })}>
        Continue with Google
      </button>
      <form onSubmit={signIn} className="stack">
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" />
        <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit" className="wide">Sign in</button>
      </form>
      {error && <p className="error">{error}</p>}
      <div className="demo">
        <span className="muted">Demo accounts:</span>
        {DEMO.map((r) => (
          <button key={r} className="ghost small" onClick={() => signIn(undefined, `${r}@greatagent.demo`)}>{r}</button>
        ))}
      </div>
    </div>
  );
}
