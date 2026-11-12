# VERIFICATION-04: Frontend Clean Architecture — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

No aplica en este módulo (el backend se verifica en MOD-01/02/03). La capa frontend se verifica con build estricto + checklist manual + Playwright (MOD-05).

## 2. Pruebas E2E (Playwright)

Los escenarios automatizados se definen y ejecutan en MOD-05 (`qa/e2e/auditoria.spec.ts`). En este módulo se exige el **checklist manual** contra el backend corriendo con `EXTRACTOR_MODE=mock`:

- [ ] Al abrir `http://localhost:5173` se ve el empty-state con instrucciones y los 3 botones de ejemplo.
- [ ] Click en "Factura Proveedor Homologado #001": el PDF aparece en el visor y el panel derecho termina en badge `APROBADO` con 5 reglas verdes (CU-01).
- [ ] El encabezado del semáforo muestra el desglose de latencia (IA / reglas / total) en cada auditoría.
- [ ] Click en "Factura con Desvío de Monto": badge `RECHAZADO`, R3 en rojo con `DISCREPANCIA_CONTABLE` y los montos comparados en el mensaje (CU-02).
- [ ] Click en "Factura Monto Alto sin OC": `RECHAZADO` por R4 con `FALTA_ORDEN_COMPRA`.
- [ ] Subir un PDF propio: valida formato/tamaño en cliente (rechazo inmediato de > 5 MB) y muestra el resultado de la auditoría.
- [ ] El panel "Ver JSON Estructurado (Pydantic)" despliega el JSON y el botón "Copiar" funciona (CU-03).
- [ ] El historial lista las auditorías de la sesión con latencia en ms; al seleccionar una fila se recarga su detalle (CU-04).
- [ ] Subir un archivo no-PDF o > 5 MB: banner de error con código, sin perder el estado de pantalla (CU-05).
- [ ] Durante la auditoría: spinner visible y botones deshabilitados (sin doble submit).

> **Evidencia MOD-04 (a nivel API/contrato, backend mock por el proxy de Vite :5173):**
> los 10 ítems quedan **pendientes de pasada visual** (2 min de Kevin, o automatizados en
> MOD-05 con Playwright — esa suite cubre exactamente estos escenarios). Lo que ya está
> verificado con HTTP real en esta sesión:
> - `GET /api/v1/ejemplos` por proxy → 200 con los 3 ejemplos (`id`, `nombre`, `descripcion`, `resultado_esperado`, `url_pdf`).
> - Flujo completo `auditarEjemplo` (GET pdf → blob → `POST /auditar` multipart) con el ejemplo aprobado → `200 APROBADO`, 5 reglas verdes, latencias `(IA 0 ms · reglas 4 ms · total 57 ms)` e `id aud_*`.
> - Camino RECHAZADO verificado con backend en `:8001` y `MOCK_VARIANT=rechazado` → `RECHAZADO` con R3 roja: `DISCREPANCIA_CONTABLE`, montos comparados en el mensaje y 4 reglas verdes. *Nota:* con la variante default (`MOCK_VARIANT=aprobada`) **todos** los PDFs auditan APROBADO — el mock es determinista y no parsea contenido (RN-2-05, ADR-02-05); R4 (`FALTA_ORDEN_COMPRA`) solo se observa con `EXTRACTOR_MODE=llm` (pendiente de key, igual que la verificación de MOD-02 §2).
> - Errores de contrato → `422 {"error":{"codigo":"PDF_INVALIDO",…}}` y `413 {"error":{"codigo":"ARCHIVO_MUY_GRANDE",…}}` con el cuerpo exacto que `BannerError` renderiza.
> - `GET /historial?limit=20&offset=0` → 5 filas **sin** `json_crudo_ia`, con latencia ms; `GET /historial/{id}` → detalle **con** JSON crudo y `datos_extraidos` con las 9 claves del espejo TS; `GET /historial/aud_inexistente` → `404 AUDITORIA_NO_ENCONTRADO`… (`AUDITORIA_NO_ENCONTRADA`).
> - Validación client-side implementada en `apiClient.validarPdf` (formato PDF + tope 5 MB, RN-4-03) y spinner/botones deshabilitados vía `auditando` en `BarraSuperior` + `EsqueletoCarga`.

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo.

## 4. Registro de Decisiones de Arquitectura (ADR Log)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `fetch` nativo sin axios | 1 API, ~6 endpoints; menos dependencias para un PoC. | Wrapper propio con normalización de errores. |
| 2026-11-12 | Sin router ni store global | Pantalla única con panel de historial; React state + hooks alcanza. | Menos boilerplate; si crece a multi-página, ADR de migración. |
| 2026-11-12 | Visor con `iframe` (sin pdf.js) | Los 3 ejemplos son PDFs digitales simples; pdf.js suma peso innecesario al MVP. | Si aparecen PDFs problemáticos, se evalúa `pdf.js` con ADR. |
| 2026-11-12 | Ejemplos auditados bajando el PDF y re-enviándolo | Un solo contrato de auditoría (`POST /auditar` multipart) sin endpoint "auditar ejemplo" extra. | 1 ida y vuelta extra, despreciable en local. |
| 2026-11-12 | **ADR-04-05:** espejo de tipos ajustado al contrato real de la API (`url_pdf` en `Ejemplo`, `cuit_emisor`/`monto_total` planos, `detalles` en reglas, `R0` incluido, `resultado_esperado: string`, montos `number`). | DESIGN-04 §2 pedía "fuente única: la API"; los DTOs reales de MOD-03 (fuente de verdad verificada por HTTP) difieren levemente del boceto del design. | Los componentes renderizan el contrato real; sin cambios de backend. |
| 2026-11-12 | **ADR-04-06:** `VITE_API_URL` vacío → base `/api/v1` (proxy de Vite del MOD-00 T-07) en lugar de `http://localhost:8000/api/v1` directo. | Respeta la convención del scaffold y evita CORS en desarrollo; en deploy (Vercel) se define `VITE_API_URL` absoluta. | Solo configuración del cliente; contrato API intacto. |
| 2026-11-12 | **ADR-04-07:** verificación visual del checklist §2 diferida a la suite Playwright de MOD-05 (que automatiza estos 10 escenarios); en MOD-04 se verificaron a nivel API/contrato con HTTP real. | No hay navegador/headless disponible sin agregar dependencias no declaradas (MOD-05 las declara). | Checklist §2 y DoD ítems 3–4 quedan a la pasada visual de Kevin o a MOD-05. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] `npm run build` (tsc strict) y `npm run lint` en verde.
- [ ] Checklist manual §2 completo en verde con backend en modo mock. *(código 100% y verificación a nivel API/contrato en verde — ver evidencia §2; pasada visual pendiente: Kevin (2 min) o MOD-05 Playwright, ADR-04-07)*
- [ ] Layout de dos columnas estable a 1024px y 1920px de ancho. *(implementado con grid `lg:grid-cols-[2fr_3fr]` que se apila bajo 1024px; verificación visual pendiente, ADR-04-07)*
- [x] Ninguna lógica de negocio duplicada en el cliente (grep: solo render de lo que devuelve la API).
