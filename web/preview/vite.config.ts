import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

const here = (p: string) => fileURLToPath(new URL(p, import.meta.url));

// Dev-only screenshot harness: same app, but "./lib" resolves to static fixtures instead of Supabase.
export default defineConfig({
  root: here("."),
  plugins: [react()],
  resolve: { alias: [{ find: /^\.\/lib$/, replacement: here("./mock-lib.ts") }] },
  server: { host: "127.0.0.1", fs: { allow: [here("..")] } },
});
