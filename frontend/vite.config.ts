import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// T-07: el frontend llama a /api y Vite lo redirige al backend (:8000 por
// defecto). El E2E de Playwright apunta su backend efímero vía VITE_PROXY_TARGET
// (puertos exclusivos del E2E — ADR-05-09); el uso manual no cambia.
const PROXY_TARGET = process.env.VITE_PROXY_TARGET ?? "http://localhost:8000";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": {
        target: PROXY_TARGET,
        changeOrigin: true,
      },
    },
  },
});
