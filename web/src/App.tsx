import { useEffect, useState } from "react";
import { isStaff, supabase, useSession, type Profile } from "./lib";
import Login from "./Login";
import Ops from "./Ops";
import PartyView from "./PartyView";

const ROLE_LABEL: Record<string, string> = {
  admin: "Admin", coordinator: "Desk coordinator", customer: "Customer", driver: "Driver",
  depot: "Depot / pickup point", merchant: "Merchant / partner",
};

export default function App() {
  const session = useSession();
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
  if (error) return <div className="center">{error} <button onClick={() => supabase.auth.signOut()}>Sign out</button></div>;
  if (!profile) return <div className="center muted">Loading profile…</div>;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Rivet Delivery Desk</div>
        <div className="who">
          <span className="pill">{ROLE_LABEL[profile.role]}</span>
          <span>{profile.party_name || profile.display_name || profile.email}</span>
          <button className="ghost" onClick={() => supabase.auth.signOut()}>Sign out</button>
        </div>
      </header>
      {isStaff(profile.role) ? <Ops profile={profile} /> : <PartyView profile={profile} />}
    </div>
  );
}
