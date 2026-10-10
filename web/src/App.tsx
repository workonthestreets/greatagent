import { useEffect, useState } from "react";
import { isStaff, signOut, supabase, useSession, type Profile } from "./lib";
import Login from "./Login";
import Ops from "./Ops";
import PartyView from "./PartyView";
import { Mark } from "./icons";

const ROLE_LABEL: Record<string, string> = {
  admin: "Admin", coordinator: "Desk coordinator", customer: "Customer", driver: "Driver",
  depot: "Depot / pickup point", merchant: "Merchant / partner",
};

const VIEW_NAME: Record<string, string> = {
  admin: "Desk", coordinator: "Desk", customer: "My deliveries", driver: "My stops",
  depot: "Shipments at my site", merchant: "Cases on my orders",
};

/** `initialCase` preselects a case (used by the screenshot preview); undefined in production. */
export default function App({ initialCase }: { initialCase?: string } = {}) {
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

  if (session === undefined) return <div className="page framed app"><p className="center text-muted state">Loading…</p></div>;
  if (!session) return <Login />;
  if (error) return (
    <div className="page framed app">
      <div className="center state">
        <p>{error}</p>
        <button className="btn btn--secondary" onClick={() => signOut()}>Sign out</button>
      </div>
    </div>
  );
  if (!profile) return <div className="page framed app"><p className="center text-muted state">Loading profile…</p></div>;

  return (
    <div className="page framed app">
      <nav className="nav">
        <div className="nav__links">
          <a className="nav__link nav__link--current" href="#top">{VIEW_NAME[profile.role]}</a>
          <span className="nav__who">{profile.party_name || profile.display_name || profile.email}</span>
        </div>
        <span className="nav__mark" aria-label="Rivet Delivery Desk" role="img"><Mark /></span>
        <div className="nav__auth">
          <span className="nav__role">{ROLE_LABEL[profile.role]}</span>
          <button className="btn btn--secondary" onClick={() => signOut()}>Sign out</button>
        </div>
      </nav>
      {isStaff(profile.role)
        ? <Ops profile={profile} initialCase={initialCase} />
        : <PartyView profile={profile} initialCase={initialCase} />}
    </div>
  );
}
