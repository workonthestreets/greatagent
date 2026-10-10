import { useCallback, useEffect, useState } from "react";
import {
  fmtTime, hub, type MedalProgress, type MerchItem, type Profile, type RedeemResponse, type RewardsMe, type TeamRow,
} from "./lib";
import { MedalIcon } from "./icons";
import { Status } from "./ui";

const ROLE_WORD: Record<string, string> = { admin: "Admin", coordinator: "Coordinator" };
const fmtDate = (ts: string) => new Date(ts).toLocaleDateString(undefined, { day: "numeric", month: "short" });

/** Coins and medals earned on the desk, the merch shop, and (admins) the team leaderboard. No band: the balance is the focal point. */
export default function Rewards({ profile }: { profile: Profile }) {
  const [me, setMe] = useState<RewardsMe | null>(null);
  const [merch, setMerch] = useState<MerchItem[]>([]);
  const [team, setTeam] = useState<TeamRow[] | null>(null);
  const [err, setErr] = useState("");
  const isAdmin = profile.role === "admin";

  const load = useCallback(async () => {
    try {
      const [m, items] = await Promise.all([hub("/api/rewards/me"), hub("/api/merch")]);
      setMe(m as RewardsMe);
      setMerch(items as MerchItem[]);
      if (isAdmin) setTeam((await hub("/api/rewards/team")) as TeamRow[]);
      setErr("");
    } catch (e) {
      setErr((e as Error).message);
    }
  }, [isAdmin]);

  useEffect(() => { load(); }, [load]);

  const earned = me?.medals.filter((m) => m.earned_at).length ?? 0;

  return (
    <main className="view rewards" id="top">
      <header className="view-head">
        <h1 className="headline-lg">Medals and <span className="emphasis">coins</span>.</h1>
        <p className="text-muted body-lg">
          Every decision on the desk earns coins: 15 for an approval, 10 for a rejection with a reason. Spend them on desk merch.
        </p>
      </header>

      {err && <p className="error-text rewards__error" role="alert">{err}</p>}
      {!me && !err && <p className="text-muted empty">Loading…</p>}

      {me && (
        <>
          <section className="balance" aria-label="Coin balance">
            <p className="balance__figure">{me.balance}</p>
            <p className="balance__unit">coins</p>
            <p className="text-muted body-sm">{me.earned_total} earned in total</p>
          </section>

          <section className="rewards__section" aria-labelledby="medals-title">
            <div className="section-head">
              <h2 className="section-title" id="medals-title">Medals</h2>
              <span className="text-muted body-sm">{earned} of {me.medals.length} earned</span>
            </div>
            <ul className="medals">
              {me.medals.map((m) => <MedalTile key={m.id} medal={m} />)}
            </ul>
          </section>

          <section className="rewards__section" aria-labelledby="shop-title">
            <div className="section-head">
              <h2 className="section-title" id="shop-title">Desk merch</h2>
              <span className="text-muted body-sm">Paid in coins</span>
            </div>
            <ul className="shop">
              {merch.map((item) => <ShopItem key={item.id} item={item} balance={me.balance} onRedeemed={load} />)}
            </ul>
          </section>

          <section className="rewards__section" aria-labelledby="orders-title">
            <h2 className="section-title" id="orders-title">Your orders</h2>
            {me.orders.length ? (
              <div className="card card--table">
                <table className="tbl">
                  <thead><tr><th>Item</th><th>Coins</th><th>Status</th><th>Placed</th></tr></thead>
                  <tbody>
                    {me.orders.map((o) => (
                      <tr key={o.id}>
                        <td className="tbl__id">{o.item_name}</td>
                        <td className="mono">{o.coins}</td>
                        <td><Status status={o.status} /></td>
                        <td className="nowrap text-muted">{fmtTime(o.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <p className="text-muted empty">No orders yet.</p>}
          </section>

          {isAdmin && team && (
            <section className="rewards__section" aria-labelledby="team-title">
              <h2 className="section-title" id="team-title">Team</h2>
              <div className="card card--table">
                <table className="tbl tbl--team">
                  <thead><tr><th>Name</th><th>Role</th><th>Coins</th><th>Medals</th><th>Decisions</th></tr></thead>
                  <tbody>
                    {team.map((t) => (
                      <tr key={t.profile_id} className={t.profile_id === profile.id ? "is-current" : ""}>
                        <td className="tbl__id">{t.display_name}</td>
                        <td className="text-muted">{ROLE_WORD[t.role] ?? t.role}</td>
                        <td className="mono">{t.balance}</td>
                        <td className="mono">{t.medals}</td>
                        <td className="mono">{t.decisions}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}

function MedalTile({ medal: m }: { medal: MedalProgress }) {
  const done = !!m.earned_at;
  const pct = Math.min(100, Math.round((m.progress / Math.max(1, m.threshold)) * 100));
  return (
    <li className={`medal ${done ? "medal--earned" : ""}`}>
      <span className="medal__icon"><MedalIcon name={m.icon} size={20} /></span>
      <div className="medal__text">
        <p className="medal__title">{m.title}</p>
        <p className="medal__desc">{m.description}</p>
        {done ? (
          <p className="medal__when">Earned {fmtDate(m.earned_at!)}</p>
        ) : (
          <div className="medal__progress">
            <span className="medal__bar" aria-hidden="true"><span style={{ width: `${pct}%` }} /></span>
            <span>{Math.min(m.progress, m.threshold)} of {m.threshold}</span>
          </div>
        )}
      </div>
    </li>
  );
}

function ShopItem({ item, balance, onRedeemed }: { item: MerchItem; balance: number; onRedeemed: () => void }) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const out = item.stock <= 0;
  const short = balance < item.price_coins;
  const redeem = async () => {
    setBusy(true);
    setMsg("");
    try {
      const r = (await hub(`/api/merch/${item.id}/redeem`, {})) as RedeemResponse;
      setMsg(`Ordered. ${r.balance} coins left.`);
      onRedeemed();
    } catch (e) {
      setMsg((e as Error).message);
    }
    setBusy(false);
  };
  return (
    <li className="card shop__item">
      <p className="shop__name">{item.name}</p>
      <p className="shop__desc">{item.description}</p>
      <div className="shop__foot">
        <span className="shop__price">{item.price_coins} <span>coins</span></span>
        <button className="btn btn--primary btn--sm" disabled={busy || out || short} onClick={redeem}>
          {busy ? "Redeeming…" : "Redeem"}
        </button>
      </div>
      <p className="shop__stock">
        {msg || (out ? "Out of stock" : short ? `${item.stock} left. ${item.price_coins - balance} more coins to go` : `${item.stock} left`)}
      </p>
    </li>
  );
}
