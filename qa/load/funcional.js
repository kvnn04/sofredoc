/**
 * k6 FUNCIONAL: valida el CONTRATO de la API bajo carga (no solo códigos 200).
 *
 * RN-5-01: corre EXCLUSIVAMENTE contra un backend con `EXTRACTOR_MODE=mock`
 * (determinismo y costo cero de IA). Tres escenarios seleccionables con la
 * variable `ESCENARIO` (default `todo` = los 3 en paralelo):
 *
 *   - `contrato`: los 6 endpoints del cheat sheet con asserts de contenido
 *     (health en modo mock, catálogo con `resultado_esperado`, PDF servido con
 *     magia `%PDF`, auditoría con id `aud_*` y latencias, listado de historial
 *     SIN `json_crudo_ia` y detalle CON `json_crudo_ia`).
 *   - `matriz`: la matriz de verdad — los 3 ejemplos + el remito fixture del
 *     E2E (fuente única de verdad, ADR-05-10): APROBADO con 5 reglas ✅,
 *     RECHAZADO solo-R3, RECHAZADO solo-R4 y RECHAZADO con exactamente 1 regla
 *     (R0 `REMITO_NO_AUDITABLE`, sin cortocircuito evaluado como 1 fila).
 *   - `errores`: los 4 caminos de error del contrato §3 — `.txt` → 422
 *     `PDF_INVALIDO`, blob 5.5 MB → 413 `ARCHIVO_MUY_GRANDE`, `historial/{id}`
 *     inexistente → 404 `AUDITORIA_NO_ENCONTRADA`, `ejemplos/{id}/pdf`
 *     inexistente → 404 `EJEMPLO_NO_ENCONTRADO`.
 *
 * Umbrales: `checks` > 99% (un 200 con JSON malformado cuenta como fallo) y
 * p95 < 500 ms. El `http_req_failed` se thresholdiza POR ESCENARIO
 * (`{scenario:contrato}` / `{scenario:matriz}`): en `errores` TODOS los
 * requests son 4xx esperados (no son fallos de disponibilidad; los checks
 * validan el cuerpo del error).
 *
 * Carga moderada por diseño (ADR-05-10): pausa de 1 s por iteración — el test
 * mantiene ~14 VUs en vuelo sin saturar el lock de la SQLite compartida
 * (techo ~165 req/s, ADR-05-06). La SATURACIÓN la mide `stress_test.js`
 * (rampa a 50 VUs); este script mide CORRECTIÓN del contrato bajo concurrencia.
 *
 * Ejecución (backend mock con BD efímera — ver qa/README.md):
 *   k6 run qa/load/funcional.js                          # completo (~2 min)
 *   SMOKE=1 k6 run qa/load/funcional.js                  # smoke CI (~30 s)
 *   ESCENARIO=matriz k6 run qa/load/funcional.js         # solo un escenario
 *   ESCENARIO=errores SMOKE=1 k6 run qa/load/funcional.js
 */
import http from "k6/http";
import { check, sleep } from "k6";

const COMPLETO = {
  contrato: { executor: "constant-vus", vus: 10, duration: "2m", exec: "contrato" },
  matriz: { executor: "constant-vus", vus: 2, duration: "2m", exec: "matriz" },
  errores: { executor: "constant-vus", vus: 2, duration: "2m", exec: "errores" },
};
const SMOKE_CI = {
  contrato: { executor: "constant-vus", vus: 6, duration: "30s", exec: "contrato" },
  matriz: { executor: "constant-vus", vus: 2, duration: "30s", exec: "matriz" },
  errores: { executor: "constant-vus", vus: 2, duration: "30s", exec: "errores" },
};

const PERFIL = __ENV.SMOKE === "1" ? SMOKE_CI : COMPLETO;
const ELEGIDO = __ENV.ESCENARIO || "todo";
if (ELEGIDO !== "todo" && !(ELEGIDO in PERFIL)) {
  throw new Error(
    `ESCENARIO='${ELEGIDO}' inválido; válidos: todo | ${Object.keys(PERFIL).join(" | ")}`,
  );
}

export const options = {
  scenarios: ELEGIDO === "todo" ? PERFIL : { [ELEGIDO]: PERFIL[ELEGIDO] },
  thresholds: {
    checks: ["rate>0.99"], // el contenido importa: un 200 malformado es fallo
    "http_req_failed{scenario:contrato}": ["rate<0.01"],
    "http_req_failed{scenario:matriz}": ["rate<0.01"],
    http_req_duration: ["p(95)<500"], // modo mock
  },
};

const BASE = __ENV.BASE_URL || "http://localhost:8000/api/v1";
const PDF_APROBADA = open("../../backend/data/ejemplos/factura-aprobada-001.pdf", "b");
const PDF_DESVIO = open("../../backend/data/ejemplos/factura-desvio-monto.pdf", "b");
const PDF_MONTO_ALTO = open("../../backend/data/ejemplos/factura-monto-alto-sin-oc.pdf", "b");
const PDF_REMITO = open("../../qa/e2e/fixtures/remito-transporte-2026.pdf", "b");
// ArrayBuffer de 5.5 MB > tope de 5 MB: dispara el 413 server-side (k6 no tiene
// Buffer; el ArrayBuffer zero-filled basta porque el contenido no se lee).
const BLOB_GRANDE = new ArrayBuffer(5.5 * 1024 * 1024);

/** POST /auditar con un archivo binario (multipart `file`). */
function auditar(datos, nombre) {
  return http.post(`${BASE}/auditar`, { file: http.file(datos, nombre, "application/pdf") });
}

/** POST /auditar con un cuerpo/texto cualquiera (para errores de formato). */
function auditarTexto(datos, nombre, tipo) {
  return http.post(`${BASE}/auditar`, { file: http.file(datos, nombre, tipo) });
}

/** Pausa por iteración: carga moderada, sin saturar la SQLite (ver header). */
const PAUSA = 1;

// ---------------------------------------------------------------------------
// Escenario `contrato`: los 6 endpoints con asserts de contenido
// ---------------------------------------------------------------------------
export function contrato() {
  const salud = http.get(`${BASE}/health`);
  check(salud, {
    "health 200": (r) => r.status === 200,
    "health modo mock (RN-5-01)": (r) => r.json("extractor_mode") === "mock",
    "health status ok": (r) => r.json("status") === "ok",
  });

  const catalogo = http.get(`${BASE}/ejemplos`);
  check(catalogo, {
    "ejemplos 200": (r) => r.status === 200,
    "ejemplos son 3": (r) => (r.json() || []).length === 3,
    "ejemplos con resultado_esperado": (r) => (r.json() || []).every((e) => !!e.resultado_esperado),
  });

  for (const ejemplo of catalogo.json() || []) {
    const pdf = http.get(`${BASE}/ejemplos/${ejemplo.id}/pdf`);
    check(pdf, {
      [`pdf ${ejemplo.id} 200`]: (r) => r.status === 200,
      [`pdf ${ejemplo.id} es application/pdf`]: (r) =>
        (r.headers["Content-Type"] || "").includes("application/pdf"),
      [`pdf ${ejemplo.id} con magia %PDF`]: (r) =>
        typeof r.body === "string" ? r.body.startsWith("%PDF") : new Uint8Array(r.body)[0] === 0x25,
    });
  }

  const auditoria = auditar(PDF_APROBADA, "factura.pdf");
  const id = auditoria.json("id");
  check(auditoria, {
    "auditar 200": (r) => r.status === 200,
    "auditar estado APROBADO": (r) => r.json("estado") === "APROBADO",
    "auditar 5 reglas": (r) => (r.json("reglas_evaluadas") || []).length === 5,
    "auditar id aud_*": (r) => /^aud_[0-9a-f]{8}$/.test(r.json("id") || ""),
    "auditar latencias numericas": (r) =>
      typeof r.json("latencia_extraccion_ms") === "number" &&
      typeof r.json("latencia_reglas_ms") === "number" &&
      typeof r.json("tiempo_ejecucion_ms") === "number",
  });

  const listado = http.get(`${BASE}/historial?limit=20&offset=0`);
  check(listado, {
    "historial 200": (r) => r.status === 200,
    "historial sin json_crudo_ia": (r) =>
      (r.json() || []).every((item) => !("json_crudo_ia" in item)),
    "historial con latencia en ms": (r) =>
      (r.json() || []).every((item) => typeof item.tiempo_ejecucion_ms === "number"),
  });

  if (id) {
    const detalle = http.get(`${BASE}/historial/${id}`);
    check(detalle, {
      "detalle 200": (r) => r.status === 200,
      "detalle con json_crudo_ia": (r) => !!r.json("json_crudo_ia"),
      "detalle mismo id": (r) => r.json("id") === id,
    });
  }

  sleep(PAUSA);
}

// ---------------------------------------------------------------------------
// Escenario `matriz`: la matriz de verdad bajo carga (3 ejemplos + remito)
// ---------------------------------------------------------------------------
export function matriz() {
  const aprobada = auditar(PDF_APROBADA, "factura-aprobada-001.pdf");
  check(aprobada, {
    "matriz aprobada → APROBADO": (r) => r.json("estado") === "APROBADO",
    "matriz aprobada → 5 reglas todas ✅": (r) =>
      (r.json("reglas_evaluadas") || []).length === 5 &&
      (r.json("reglas_evaluadas") || []).every((regla) => regla.aprobado),
  });

  const desvio = auditar(PDF_DESVIO, "factura-desvio-monto.pdf");
  check(desvio, {
    "matriz desvio → RECHAZADO": (r) => r.json("estado") === "RECHAZADO",
    "matriz desvio → solo R3": (r) => {
      const caidas = (r.json("reglas_evaluadas") || []).filter((regla) => !regla.aprobado);
      return caidas.length === 1 && caidas[0].codigo_error === "DISCREPANCIA_CONTABLE";
    },
  });

  const montoAlto = auditar(PDF_MONTO_ALTO, "factura-monto-alto-sin-oc.pdf");
  check(montoAlto, {
    "matriz monto alto → RECHAZADO": (r) => r.json("estado") === "RECHAZADO",
    "matriz monto alto → solo R4": (r) => {
      const caidas = (r.json("reglas_evaluadas") || []).filter((regla) => !regla.aprobado);
      return caidas.length === 1 && caidas[0].codigo_error === "FALTA_ORDEN_COMPRA";
    },
  });

  const remito = auditar(PDF_REMITO, "remito-transporte-2026.pdf");
  check(remito, {
    "matriz remito → RECHAZADO": (r) => r.json("estado") === "RECHAZADO",
    "matriz remito → 1 sola regla (R0)": (r) => {
      const reglas = r.json("reglas_evaluadas") || [];
      return reglas.length === 1 && reglas[0].codigo === "R0";
    },
    "matriz remito → REMITO_NO_AUDITABLE": (r) =>
      r.json("reglas_evaluadas.0.codigo_error") === "REMITO_NO_AUDITABLE",
  });

  sleep(PAUSA);
}

// ---------------------------------------------------------------------------
// Escenario `errores`: los 4 caminos de error del contrato §3
// ---------------------------------------------------------------------------
export function errores() {
  const noPdf = auditarTexto("esto no es un pdf", "notas.txt", "text/plain");
  check(noPdf, {
    "txt → 422": (r) => r.status === 422,
    "txt → PDF_INVALIDO": (r) => r.json("error.codigo") === "PDF_INVALIDO",
    "txt → mensaje presente": (r) => (r.json("error.mensaje") || "").length > 0,
  });

  const grande = http.post(`${BASE}/auditar`, {
    file: http.file(BLOB_GRANDE, "factura-grande.pdf", "application/pdf"),
  });
  check(grande, {
    "blob 5.5MB → 413": (r) => r.status === 413,
    "blob 5.5MB → ARCHIVO_MUY_GRANDE": (r) => r.json("error.codigo") === "ARCHIVO_MUY_GRANDE",
  });

  const auditoriaFantasma = http.get(`${BASE}/historial/aud_inexistente`);
  check(auditoriaFantasma, {
    "historial inexistente → 404": (r) => r.status === 404,
    "historial inexistente → codigo tipado": (r) =>
      r.json("error.codigo") === "AUDITORIA_NO_ENCONTRADA",
  });

  const ejemploFantasma = http.get(`${BASE}/ejemplos/id-falso/pdf`);
  check(ejemploFantasma, {
    "ejemplo inexistente → 404": (r) => r.status === 404,
    "ejemplo inexistente → codigo tipado": (r) => r.json("error.codigo") === "EJEMPLO_NO_ENCONTRADO",
  });

  sleep(PAUSA);
}
