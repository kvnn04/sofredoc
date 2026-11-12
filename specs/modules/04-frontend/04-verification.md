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

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo.

## 4. Registro de Decisiones de Arquitectura (ADR Log)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `fetch` nativo sin axios | 1 API, ~6 endpoints; menos dependencias para un PoC. | Wrapper propio con normalización de errores. |
| 2026-11-12 | Sin router ni store global | Pantalla única con panel de historial; React state + hooks alcanza. | Menos boilerplate; si crece a multi-página, ADR de migración. |
| 2026-11-12 | Visor con `iframe` (sin pdf.js) | Los 3 ejemplos son PDFs digitales simples; pdf.js suma peso innecesario al MVP. | Si aparecen PDFs problemáticos, se evalúa `pdf.js` con ADR. |
| 2026-11-12 | Ejemplos auditados bajando el PDF y re-enviándolo | Un solo contrato de auditoría (`POST /auditar` multipart) sin endpoint "auditar ejemplo" extra. | 1 ida y vuelta extra, despreciable en local. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [ ] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [ ] `npm run build` (tsc strict) y `npm run lint` en verde.
- [ ] Checklist manual §2 completo en verde con backend en modo mock.
- [ ] Layout de dos columnas estable a 1024px y 1920px de ancho.
- [ ] Ninguna lógica de negocio duplicada en el cliente (grep: solo render de lo que devuelve la API).
