# TASKS-04: Frontend Clean Architecture — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que el build de TypeScript sigue pasando (`npm run build`).

## Fase 1: Dominio e Infraestructura (Contrato)

- [x] **T-01:** Crear `frontend/src/domain/types.ts` con el espejo exacto del contrato API (MOD-03 §3) según `02-design.md` §2.
- [x] **T-02:** Implementar `frontend/src/infrastructure/apiClient.ts`: base URL desde `VITE_API_URL`, wrapper `fetch` con normalización de errores a `ErrorApi`, y las 6 funciones del contrato (auditar archivo/ejemplo, ejemplos, pdf, historial, detalle).
- [x] **T-03:** Implementar `auditarEjemplo(id)`: descargar `GET /ejemplos/{id}/pdf` como blob → `File` → `POST /auditar` (un solo contrato para ejemplos y uploads).

## Fase 2: Aplicación (Hooks)

- [x] **T-04:** Implementar `useEjemplos()` (carga el catálogo al montar).
- [x] **T-05:** Implementar `useAuditoria()`: máquina de estados `idle | loading | resultado | error`, expone `auditar(ejemploId | File)`, guarda `ResultadoAuditoria` y el `pdfUrl` (blob URL o URL de ejemplo) para el visor; revoca blob URLs al reemplazar.
- [x] **T-06:** Implementar `useHistorial(limit, offset)`: listado paginado + `refrescar()` invocado tras cada auditoría exitosa.

## Fase 3: Presentación (Componentes + Layout)

- [ ] **T-07:** Implementar `App.tsx` con el layout de dos columnas de `02-design.md` §5 (grid Tailwind, visor 40% / resultados 60%, min-width útil ~1024px) y la máquina de estados visual (empty-state, skeleton de carga, resultado, error).
- [ ] **T-08:** Implementar `BarraSuperior.tsx`: título, botones de los 3 ejemplos (nombre + chip del resultado esperado), botón "Subir PDF" con `input[type=file] accept="application/pdf"` y validación client-side de 5 MB.
- [ ] **T-09:** Implementar `VisorPDF.tsx`: `iframe` con `src` del blob/URL de ejemplo, altura completa de columna, fallback de texto si el navegador bloquea el embed.
- [ ] **T-10:** Implementar `SemaforoReglas.tsx`: badge global (`APROBADO` verde / `RECHAZADO` rojo) con `CheckCircle2`/`XCircle`, **desglose de latencia por etapa** (IA / reglas / total), id de auditoría, y una fila por regla con chip de código, nombre, mensaje y `codigo_error` en monospace rojo si falla.
- [ ] **T-11:** Implementar `TablaDatos.tsx`: cabecera de comprobante + tabla de ítems + fila de total, montos formateados `es-AR`, estado vacío si `datos_extraidos` es `null`.
- [ ] **T-12:** Implementar `JsonInspector.tsx`: panel plegable "Ver JSON Estructurado (Pydantic)" con `datos_extraidos` y `json_crudo_ia` en `<pre>` con scroll, y botón "Copiar" (`navigator.clipboard`).
- [ ] **T-13:** Implementar `Historial.tsx`: tabla (fecha, archivo, estado con color, latencia ms) paginada simple, fila seleccionada re-carga la auditoría completa vía `obtenerAuditoria(id)`.
- [ ] **T-14:** Implementar `BannerError.tsx`: muestra `error.codigo` + `error.mensaje` para `413/422/502` sin destruir el estado previo de la pantalla.

## Fase 4: Pulido

- [ ] **T-15:** Formateo de montos y fechas con `Intl` (`es-AR`), tooltips e `aria-labels`, y limpieza de estados muertos.
- [ ] **T-16:** Verificar `npm run build` (tsc strict) y `npm run lint` en verde; quickstart actualizado en `README.md`.
