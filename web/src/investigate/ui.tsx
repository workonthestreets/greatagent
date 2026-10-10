/** Confidence badge from web_v2 (v2's other ui pieces already exist in ../ui). */
export function Conf({ level }: { level: "high" | "medium" | "low" }) {
  return (
    <span className={`conf conf--${level}`}>
      <span className="conf__dot" aria-hidden="true" />
      {level.charAt(0).toUpperCase() + level.slice(1)} confidence
    </span>
  );
}
