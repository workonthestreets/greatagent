import { useEffect, useState } from "react";
import { DEMO_ROLES, go as goPath, isStaff, signOut, supabase, switchAccount, usePath, useSession, type Profile, type Role } from "./lib";
import AgentsPage from "./AgentPage";
import InvestigatePage from "./investigate/InvestigatePage";
import Login from "./Login";
import Ops from "./Ops";
import Rewards from "./Rewards";
import CustomerPortal from "./CustomerPortal";
import DriverPortal from "./DriverPortal";
import DepotPortal from "./DepotPortal";
import MerchantPortal from "./MerchantPortal";
import { Mark } from "./icons";

const ROLE_LABEL: Record<string, string> = {
  admin: "Admin", coordinator: "Desk coordinator", customer: "Customer", driver: "Driver",
  depot: "Depot / pickup point", merchant: "Merchant / partner",
};

const VIEW_NAME: Record<string, string> = {
  admin: "Desk", coordinator: "Desk", customer: "My deliveries", driver: "My stops",
  depot: "Shipments at my site", merchant: "Cases on my orders",
};

const PORTALS = { customer: CustomerPortal, driver: DriverPortal, depot: DepotPortal, merchant: MerchantPortal };

type Page = "desk" | "rewards" | "agents" | "investigate";

/** `initialCase` / `initialPage` preselect a case or a staff page (used by the screenshot preview); undefined in production. */
export default function App({ initialCase, initialPage = "desk" }: { initialCase?: string; initialPage?: Page } = {}) {
  const session = useSession();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState("");
  const [statePage, setPage] = useState<Page>(initialPage);
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState("");
  // /agents and /agents/<case id> are real URLs (shareable, back button works); Desk and Rewards stay in-app pages.
  const path = usePath();
  const agentsRoute = /^\/agents?(\/|$)/.test(path);
  const agentCase = decodeURIComponent(path.match(/^\/agents?\/([^/]+)/)?.[1] ?? "") || null;
  const investigateRoute = /^\/investigate\/?$/.test(path);
  const page: Page = agentsRoute ? "agents" : investigateRoute ? "investigate" : statePage;

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

  const staff = isStaff(profile.role);
  const go = (p: Page) => (e: React.MouseEvent) => {
    e.preventDefault();
    if (p === "agents") goPath("/agents");
    else if (p === "investigate") goPath("/investigate");
    else { if (agentsRoute || investigateRoute) goPath("/"); setPage(p); }
    window.scrollTo({ top: 0 });
  };
  const Portal = PORTALS[profile.role as keyof typeof PORTALS] ?? CustomerPortal;

  return (
    <div className="page framed app">
      <nav className="nav">
        <div className="nav__links">
          {staff ? (
            <>
              {page === "desk"
                ? <a className="nav__link nav__mobile" href="#rewards" onClick={go("rewards")}>Rewards</a>
                : <a className="nav__link nav__mobile" href="#top" onClick={go("desk")}>Desk</a>}
              <a className={`nav__link ${page === "desk" ? "nav__link--current" : ""}`} href="#top" onClick={go("desk")}
                aria-current={page === "desk" ? "page" : undefined}>Desk</a>
              <a className={`nav__link ${page === "agents" ? "nav__link--current" : ""}`} href="/agents" onClick={go("agents")}
                aria-current={page === "agents" ? "page" : undefined}>Agents</a>
              <a className={`nav__link ${page === "investigate" ? "nav__link--current" : ""}`} href="/investigate" onClick={go("investigate")}
                aria-current={page === "investigate" ? "page" : undefined}>Investigate</a>
              <a className={`nav__link ${page === "rewards" ? "nav__link--current" : ""}`} href="#rewards" onClick={go("rewards")}
                aria-current={page === "rewards" ? "page" : undefined}>Rewards</a>
            </>
          ) : <a className="nav__link nav__link--current" href="#top">{VIEW_NAME[profile.role]}</a>}
          <span className="nav__who">{profile.party_name || profile.display_name || profile.email}</span>
        </div>
        <span className="nav__mark" aria-label="Rivet Delivery Desk" role="img"><Mark /></span>
        <div className="nav__auth">
          <span className="nav__role">{ROLE_LABEL[profile.role]}</span>
          <label className="nav__switch">
            <span className="sr-only">Switch role</span>
            <select className="input input--sm" value="" disabled={switching} aria-label="Switch role"
              onChange={async (e) => {
                const role = e.target.value as Role;
                if (!role) return;
                setSwitching(true); setSwitchError("");
                const err = await switchAccount(role);
                setSwitching(false);
                if (err) setSwitchError(err);
              }}>
              <option value="">{switching ? "Switching…" : "Switch role…"}</option>
              {DEMO_ROLES.filter((r) => r !== profile.role).map((r) => <option key={r} value={r}>{ROLE_LABEL[r]}</option>)}
            </select>
          </label>
          <button className="btn btn--secondary" disabled={switching} onClick={() => signOut()}>Sign out</button>
        </div>
      </nav>
      {switchError && <p className="error-text nav__error" role="alert">Could not switch role: {switchError}</p>}
      {staff
        ? page === "agents" ? <AgentsPage caseId={agentCase} />
          : page === "investigate" ? <InvestigatePage />
          : page === "rewards" ? <Rewards profile={profile} /> : <Ops profile={profile} initialCase={initialCase} />
        : <Portal profile={profile} initialCase={initialCase} />}
    </div>
  );
}
