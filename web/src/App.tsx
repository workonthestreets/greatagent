import { useEffect, useState } from "react";
import { go, isStaff, signOut, supabase, usePath, useSession, type Profile } from "./lib";
import AgentsPage from "./AgentPage";
import Login from "./Login";
import Ops from "./Ops";
import PartyView from "./PartyView";

const ROLE_LABEL: Record<string, string> = {
  admin: "Admin", coordinator: "Desk coordinator", customer: "Customer", driver: "Driver",
  depot: "Depot / pickup point", merchant: "Merchant / partner",
};

export default function App() {
  const session = useSession();
  const path = usePath();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!session) { setProfile(null); return; }
    supabase.from("profiles").select("*").eq("id", session.user.id).single().then(({ data, error }) => {
      if (error) setError("No profile for this account yet. Ask an admin.");
      else setProfile(data as Profile);
    });
  }, [session]);

  if (session === undefined) return <div className="center muted">Loading…</div>;
  if (!session) return <Login />;
  if (error) return <div className="center">{error} <button onClick={() => signOut()}>Sign out</button></div>;
  if (!profile) return <div className="center muted">Loading profile…</div>;

  // /agents (inbox) and /agents/<case id>; the older /agent/<case id> form goes to the same place.
  const agentsRoute = /^\/agents?(\/|$)/.test(path);
  const agentCase = decodeURIComponent(path.match(/^\/agents?\/([^/]+)/)?.[1] ?? "") || null;

  return (
    <div className="app">
      <header className="topbar">
        <a className="brand" href="/" onClick={(e) => { e.preventDefault(); go("/"); }}>Rivet Delivery Desk</a>
        <div className="who">
          {isStaff(profile.role) && <nav className="nav">
            <a href="/" className={!agentsRoute ? "on" : ""} onClick={(e) => { e.preventDefault(); go("/"); }}>Dashboard</a>
            <a href="/agents" className={agentsRoute ? "on" : ""} onClick={(e) => { e.preventDefault(); go("/agents"); }}>Agents</a>
          </nav>}
          <span className="pill">{ROLE_LABEL[profile.role]}</span>
          <span>{profile.party_name || profile.display_name || profile.email}</span>
          <button className="ghost" onClick={() => signOut()}>Sign out</button>
        </div>
      </header>
      {agentsRoute && isStaff(profile.role) ? <AgentsPage caseId={agentCase} />
        : agentsRoute ? <div className="center muted">The agent view is for desk staff.</div>
        : isStaff(profile.role) ? <Ops profile={profile} /> : <PartyView profile={profile} />}
    </div>
  );
}
