"""Fill the live-desk settings in .env (and web/.env) interactively. Secrets are typed with hidden input and
written straight to the files; nothing is printed. Existing values are kept unless you type a new one.

    .venv/bin/python -m hub.setup_env
"""
from __future__ import annotations

import getpass
import secrets
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SUPABASE_REF = "yfyilhvigncdijjjrkih"


def read_env(path: Path) -> dict[str, str]:
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def write_env(path: Path, updates: dict[str, str]) -> None:
    lines = path.read_text().splitlines() if path.exists() else []
    seen = set()
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip() if "=" in line and not line.lstrip().startswith("#") else None
        if key in updates:
            lines[i] = f"{key}={updates[key]}"
            seen.add(key)
    lines += [f"{k}={v}" for k, v in updates.items() if k not in seen]
    path.write_text("\n".join(lines) + "\n")
    path.chmod(0o600)


def ask(label: str, current: str, secret: bool = False, default: str = "") -> str:
    shown = "(set, Enter to keep)" if current and secret else (f"[{current or default}]" if (current or default) else "")
    prompt = f"{label} {shown}: "
    value = (getpass.getpass(prompt) if secret else input(prompt)).strip()
    return value or current or default


def main() -> None:
    env_path = ROOT / ".env"
    env = read_env(env_path)
    print(f"Supabase project {SUPABASE_REF}: keys at "
          f"https://supabase.com/dashboard/project/{SUPABASE_REF}/settings/api-keys/legacy")

    u: dict[str, str] = {}
    u["SUPABASE_URL"] = f"https://{SUPABASE_REF}.supabase.co"
    u["SUPABASE_ANON_KEY"] = ask("Supabase anon key", env.get("SUPABASE_ANON_KEY", ""), secret=True)
    u["SUPABASE_SERVICE_ROLE_KEY"] = ask("Supabase service_role key", env.get("SUPABASE_SERVICE_ROLE_KEY", ""), secret=True)

    if not env.get("DATABASE_URL"):
        print("Database: Connect (top bar) -> Session pooler shows the host, e.g. aws-0-eu-west-2.pooler.supabase.com")
        host = input("Pooler host: ").strip()
        pw = getpass.getpass("Database password (Settings -> Database to reset if unknown): ").strip()
        if host and pw:
            u["DATABASE_URL"] = f"postgresql://postgres.{SUPABASE_REF}:{quote(pw, safe='')}@{host}:5432/postgres"

    if not env.get("ANTHROPIC_API_KEY"):
        u["ANTHROPIC_API_KEY"] = ask("Anthropic API key", "", secret=True)
    u["ANTHROPIC_WORKSPACE_ID"] = ask("Anthropic workspace ID (from Console URL)", env.get("ANTHROPIC_WORKSPACE_ID", ""), default="default")
    u["ADMIN_EMAILS"] = ask("Admin emails, comma-separated", env.get("ADMIN_EMAILS", ""))
    u["HUB_PUBLIC_URL"] = ask("Hub public URL (tunnel; blank for now)", env.get("HUB_PUBLIC_URL", ""))
    u["HUB_MCP_TOKEN"] = env.get("HUB_MCP_TOKEN") or secrets.token_hex(32)
    u["HUB_WEBHOOK_SECRET"] = env.get("HUB_WEBHOOK_SECRET") or secrets.token_hex(32)
    u["DEMO_PASSWORD"] = env.get("DEMO_PASSWORD") or secrets.token_urlsafe(9)

    write_env(env_path, {k: v for k, v in u.items() if v})
    write_env(ROOT / "web" / ".env", {
        "VITE_SUPABASE_URL": u["SUPABASE_URL"],
        "VITE_SUPABASE_ANON_KEY": u["SUPABASE_ANON_KEY"],
        "VITE_HUB_URL": u["HUB_PUBLIC_URL"] or "http://localhost:8000",
        "VITE_DEMO_PASSWORD": u["DEMO_PASSWORD"],
    })
    missing = [k for k in ("SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "DATABASE_URL", "HUB_PUBLIC_URL")
               if not (u.get(k) or env.get(k))]
    print("Wrote .env and web/.env." + (f" Still missing: {', '.join(missing)}." if missing else ""))


if __name__ == "__main__":
    main()
