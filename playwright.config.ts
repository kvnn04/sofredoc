/**
 * Config de Playwright (MOD-05 T-05, DESIGN-05 §3).
 *
 * Levanta los 2 procesos reales con `webServer` y corre contra la UI real.
 * ADR-05-09: puertos EXCLUSIVOS del E2E (backend :8010, frontend :5175) y
 * `reuseExistingServer: false` — así el E2E nunca reutiliza el backend manual
 * del desarrollador (si corre en modo `llm`, la matriz de verdad mock no aplica:
 * latencias reales, costo de créditos y BD real — bug detectado 2026-11-13 en
 * el escenario 2, que aserta los montos de la fixture mock).
 *
 * Backend en modo mock con SQLite efímera de artefacto (RN-5-05, vive en
 * `qa/artifacts/`, nunca toca `backend/data/sofredoc.db`). El comando del
 * backend la borra al inicio de cada corrida (`qa/e2e/reset-db.mjs`) para
 * reproducibilidad de cero. `retries: 0` (RN-5-06: un flake se investiga, no
 * se reintenta a ciegas).
 */
import { defineConfig } from "@playwright/test";

/** Python del backend: venv en Windows; el python global en CI/Linux. */
const PYTHON = process.platform === "win32" ? ".venv\\Scripts\\python.exe" : "python";

const PUERTO_BACKEND = 8010; // exclusivo del E2E (el manual usa 8000)
const PUERTO_FRONTEND = 5175; // exclusivo del E2E (el manual usa 5173)

export default defineConfig({
  testDir: "./qa/e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  // Los escenarios comparten la BD efímera del backend (el historial acumula).
  fullyParallel: false,
  workers: 1,
  retries: 0, // RN-5-06: sin máscara de flakes
  reporter: [["html", { open: "never", outputFolder: "qa/artifacts/playwright-report" }]],
  use: {
    baseURL: `http://localhost:${PUERTO_FRONTEND}`,
    viewport: { width: 1440, height: 900 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    // Para el botón "Copiar" del inspector de JSON (navigator.clipboard).
    permissions: ["clipboard-read", "clipboard-write"],
  },
  webServer: [
    {
      command: `node ../qa/e2e/reset-db.mjs && ${PYTHON} -m uvicorn src.main:app --port ${PUERTO_BACKEND}`,
      cwd: "./backend",
      url: `http://localhost:${PUERTO_BACKEND}/api/v1/health`,
      reuseExistingServer: false, // nunca reutilizar un backend ajeno al E2E
      timeout: 30_000,
      env: {
        EXTRACTOR_MODE: "mock",
        // `Settings.resolve_path` resuelve rutas relativas contra la raíz del repo.
        DB_PATH: "qa/artifacts/e2e-sofredoc.db",
      },
    },
    {
      command: `npm run dev -- --port ${PUERTO_FRONTEND} --strictPort`,
      cwd: "./frontend",
      url: `http://localhost:${PUERTO_FRONTEND}`,
      reuseExistingServer: false,
      timeout: 60_000,
      env: {
        // El proxy /api del frontend apunta al backend efímero del E2E.
        VITE_PROXY_TARGET: `http://localhost:${PUERTO_BACKEND}`,
      },
    },
  ],
});
