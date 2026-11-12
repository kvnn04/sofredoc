/**
 * Config de Playwright (MOD-05 T-05, DESIGN-05 §3).
 *
 * Levanta los 2 procesos reales con `webServer` (backend uvicorn en modo mock
 * con SQLite efímero de artefacto + frontend Vite) y corre contra la UI real
 * en http://localhost:5173. `retries: 0` (RN-5-06: un flake se investiga, no
 * se reintenta a ciegas).
 *
 * RN-5-05: la BD del E2E vive en `qa/artifacts/` (gitignored); nunca toca
 * `backend/data/sofredoc.db`. El comando del backend la borra al inicio de
 * cada corrida (`qa/e2e/reset-db.mjs`) para reproducibilidad de cero.
 */
import { defineConfig } from "@playwright/test";

/** Python del backend: venv en Windows; el python global en CI/Linux. */
const PYTHON = process.platform === "win32" ? ".venv\\Scripts\\python.exe" : "python";

export default defineConfig({
  testDir: "./qa/e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  // Los 4 escenarios comparten la BD efímera del backend (el historial acumula).
  fullyParallel: false,
  workers: 1,
  retries: 0, // RN-5-06: sin máscara de flakes
  reporter: [["html", { open: "never", outputFolder: "qa/artifacts/playwright-report" }]],
  use: {
    baseURL: "http://localhost:5173",
    viewport: { width: 1440, height: 900 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    // Para el botón "Copiar" del inspector de JSON (navigator.clipboard).
    permissions: ["clipboard-read", "clipboard-write"],
  },
  webServer: [
    {
      command: `node ../qa/e2e/reset-db.mjs && ${PYTHON} -m uvicorn src.main:app --port 8000`,
      cwd: "./backend",
      url: "http://localhost:8000/api/v1/health",
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      env: {
        EXTRACTOR_MODE: "mock",
        // `Settings.resolve_path` resuelve rutas relativas contra la raíz del repo.
        DB_PATH: "qa/artifacts/e2e-sofredoc.db",
      },
    },
    {
      command: "npm run dev -- --port 5173 --strictPort",
      cwd: "./frontend",
      url: "http://localhost:5173",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
});
