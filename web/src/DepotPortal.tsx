import type { Profile } from "./lib";
import { ShipmentPortal, type StatusOption } from "./portal";

const OPTIONS: StatusOption[] = [
  { status: "arrived_at_depot", label: "Arrived" },
  { status: "ready_for_collection", label: "Ready for collection" },
  { status: "collected", label: "Collected" },
];

/** Depots and pickup points: shipments held at or passing through their site, and the cases about them. */
export default function DepotPortal({ profile, initialCase }: { profile: Profile; initialCase?: string }) {
  return (
    <ShipmentPortal
      head={<>Shipments at your <span className="emphasis">site</span>.</>}
      sub="Parcels held or passing through your site, and what the desk needs from you."
      stopsTitle="At your site" options={OPTIONS} column="depot" partyName={profile.party_name}
      empty="No shipments at your site right now." initialCase={initialCase} />
  );
}
