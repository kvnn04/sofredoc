# VERIFICATION-04: Frontend Clean Architecture — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

No aplica en este módulo (el backend se verifica en MOD-01/02/03). La capa frontend se verifica con build estricto + checklist manual + Playwright (MOD-05).

## 2. Pruebas E2E (Playwright)

Los escenarios automatizados se definen y ejecutan en MOD-05 (`qa/e2e/auditoria.spec.ts`). En este módulo se exige el **checklist manual** contra el backend corriendo con `EXTRACTOR_MODE=mock`:

- [x] Al abrir `http://localhost:5173` se ve el empty-state con instrucciones y los 3 botones de ejemplo.
- [x] Click en "Factura Proveedor Homologado #001": el PDF aparece en el visor y el panel derecho termina en badge `APROBADO` con 5 reglas verdes (CU-01).
- [x] El encabezado del semáforo muestra el desglose de latencia (IA / reglas / total) en cada auditoría.
- [x] Click en "Factura con Desvío de Monto": badge `RECHAZADO`, R3 en rojo con `DISCREPANCIA_CONTABLE` y los montos comparados en el mensaje (CU-02).
- [x] Click en "Factura Monto Alto sin OC": `RECHAZADO` por R4 con `FALTA_ORDEN_COMPRA`.
- [x] Subir un PDF propio: valida formato/tamaño en cliente (rechazo inmediato de > 5 MB) y muestra el resultado de la auditoría.
- [x] El panel "Ver JSON Estructurado (Pydantic)" despliega el JSON y el botón "Copiar" funciona (CU-03).
- [x] El historial lista las auditorías de la sesión con latencia en ms; al seleccionar una fila se recarga su detalle (CU-04).
- [x] Subir un archivo no-PDF o > 5 MB: banner de error con código, sin perder el estado de pantalla (CU-05).
- [x] Durante la auditoría: spinner visible y botones deshabilitados (sin doble submit).

> **Evidencia MOD-04 (cerrado en MOD-05 vía Playwright, ADR-04-07):** los 10 ítems quedaron
> automatizados en `qa/e2e/auditoria.spec.ts` (escenarios 1–5) y pasaron en verde con
> `retries: 0`: escenarios 1–3 = ejemplos APROBADO / R3 con montos `$28.200,00` vs
> `$30.000,00` / R4 (mock por identidad de ejemplo, ADR-05-01, también cubre R4 sin key);
> escenario 4 = JSON inspector + historial; escenario 5 = empty-state, `.txt` →
> `PDF_INVALIDO`, 6 MB → `ARCHIVO_MUY_GRANDE` sin perder estado (CU-05), flujo completo
> con PDF real y estado "Auditando…" (botón deshabilitado + skeleton, latencia amplificada
> con `page.route` — backend intacto). Dos pasadas consecutivas: 33,5 s y 31,3 s (5/5).
> Verificación HTTP de contrato previa (MOD-04): `GET /api/v1/ejemplos` por proxy → 200
> con los 3 ejemplos; flujo `auditarEjemplo` completo → `200 APROBADO`; errores de
> contrato → `422 PDF_INVALIDO` / `413 ARCHIVO_MUY_GRANDE` con el cuerpo exacto que
> `BannerError` renderiza; `GET /historial` sin `json_crudo_ia` y `404
> AUDITORIA_NO_ENCONTRADA`.

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo.

## 4. Registro de Decisiones de Arquitectura (ADR Log)

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas y enlazadas por tema en [`specs/ADRs.md`](../../ADRs.md). El texto completo vive en [`specs/adr/`](../../adr/): los 3 ADRs numerados como archivos individuales y las decisiones de base en [`base-02-05-extraccion-api-ui-qa.md`](../../adr/base-02-05-extraccion-api-ui-qa.md). Esta sección queda como tabla resumen de navegación.

### Decisiones de base (sin ID)

Texto completo (motivo e impacto): [`base-02-05-extraccion-api-ui-qa.md` · MOD-04](../../adr/base-02-05-extraccion-api-ui-qa.md#mod-04-frontend-clean-architecture)

| Fecha | Decisión |
| :--- | :--- |
| 2026-11-12 | `fetch` nativo sin axios |
| 2026-11-12 | Sin router ni store global |
| 2026-11-12 | Visor con `iframe` (sin pdf.js) |
| 2026-11-12 | Ejemplos auditados bajando el PDF y re-enviándolo |

### Decisiones formales (numeradas)

| ID | Fecha | Decisión | Archivo |
| :--- | :--- | :--- | :--- |
| ADR-04-05 | 2026-11-12 | Espejo de tipos ajustado al contrato real de la API | [→](../../adr/adr-04-05-espejo-de-tipos-contrato-real.md) |
| ADR-04-06 | 2026-11-12 | VITE_API_URL vacío usa el proxy de Vite | [→](../../adr/adr-04-06-vite-api-url-y-proxy.md) |
| ADR-04-07 | 2026-11-12 | Verificación visual diferida a Playwright de MOD-05 | [→](../../adr/adr-04-07-verificacion-visual-diferida-playwright.md) |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] `npm run build` (tsc strict) y `npm run lint` en verde.
- [x] Checklist manual §2 completo en verde con backend en modo mock. *(Los 10 ítems automatizados en la suite Playwright de MOD-05 (`qa/e2e/auditoria.spec.ts`, escenarios 1–5) y en verde: 2 pasadas consecutivas 5/5 con `retries: 0` — cierra ADR-04-07.)*
- [x] Layout de dos columnas estable a 1024px y 1920px de ancho. *(Grid `lg:grid-cols-[2fr_3fr]` que se apila bajo 1024px; evidencia visual en las capturas full-page del E2E, `docs/capturas/`.)*
- [x] Ninguna lógica de negocio duplicada en el cliente (grep: solo render de lo que devuelve la API).
