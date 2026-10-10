import type { Profile } from "./lib";
import { ShipmentPortal, type StatusOption } from "./portal";

const OPTIONS: StatusOption[] = [
  { status: "out_for_delivery", label: "Out for delivery" },
  { status: "attempted", label: "Attempted" },
  { status: "delivered", label: "Delivered" },
];

/** Drivers: the stops on their route (shipments where driver_name is theirs) and the cases about them. */
export default function DriverPortal({ profile, initialCase }: { profile: Profile; initialCase?: string }) {
  return (
    <ShipmentPortal
      head={<>Stops on your <span className="emphasis">route</span>.</>}
      sub="The shipments you are carrying and the cases the desk has opened about them."
      stopsTitle="Stops" options={OPTIONS} column="driver_name" partyName={profile.party_name}
      empty="No stops on your route yet." initialCase={initialCase} />
  );
}
