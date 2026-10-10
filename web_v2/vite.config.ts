import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// /api/v2 is proxied to the stateless api_v2 service (uvicorn api_v2.app:app --port 8100)
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api/v2": { target: process.env.V2_API_URL || "http://localhost:8100", changeOrigin: true } } },
});
