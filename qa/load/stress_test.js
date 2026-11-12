/**
 * Prueba de carga del backend (DESIGN-05 §3, CU-03, RN-5-01).
 *
 * RN-5-01: corre EXCLUSIVAMENTE contra un backend con `EXTRACTOR_MODE=mock`
 * (determinismo y costo cero de IA). El flujo por iteración: `POST /auditar`
 * con el PDF del ejemplo #001 (viaja en el repo) + lecturas de `/historial` y
 * `/ejemplos`.
 *
 * Umbrales (SLOs): tasa de error < 1% y p95 < 500 ms.
 *
 * Ejecución (ver qa/README.md):
 *   k6 run qa/load/stress_test.js
 * Smoke para CI (10 VUs × 30 s):
 *   SMOKE=1 k6 run qa/load/stress_test.js      (en Windows: $env:SMOKE="1" ; …)
 */
import http from "k6/http";
import { check } from "k6";

const CARGA_COMPLETA = [
  { duration: "30s", target: 50 }, // rampa
  { duration: "1m", target: 50 }, // meseta (concurrencia objetivo)
  { duration: "15s", target: 0 }, // drenaje
];
const SMOKE_CI = [{ duration: "30s", target: 10 }];

export const options = {
  stages: __ENV.SMOKE === "1" ? SMOKE_CI : CARGA_COMPLETA,
  thresholds: {
    http_req_failed: ["rate<0.01"], // < 1% errores
    http_req_duration: ["p(95)<500"], // p95 < 500 ms (modo mock)
  },
};

const BASE = __ENV.BASE_URL || "http://localhost:8000/api/v1";
const PDF = open("../../backend/data/ejemplos/factura-aprobada-001.pdf", "b");

export default function () {
  // Auditoría (mock) — flujo principal
  const respuesta = http.post(`${BASE}/auditar`, {
    file: http.file(PDF, "factura.pdf", "application/pdf"),
  });
  check(respuesta, {
    "auditar 200": (r) => r.status === 200,
    "con 5 reglas": (r) => {
      try {
        return (r.json("reglas_evaluadas") || []).length === 5;
      } catch {
        return false;
      }
    },
  });

  // Lecturas
  check(http.get(`${BASE}/historial?limit=10`), {
    "historial 200": (r) => r.status === 200,
  });
  check(http.get(`${BASE}/ejemplos`), {
    "ejemplos 200": (r) => r.status === 200,
  });
}
