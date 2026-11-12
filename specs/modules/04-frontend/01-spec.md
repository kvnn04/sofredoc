# SPEC-04: Frontend Clean Architecture — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio

La PoC debe **demostrarse en 15 segundos**: un líder técnico o reclutador que abre la app tiene que poder auditar un comprobante sin leer documentación, viendo el documento y el dictamen de auditoría en la misma pantalla. Sin una UI operativa, el valor del motor de reglas y de la extracción IA queda invisible.

Este módulo construye la **interfaz de pantalla dividida** (visor de documento a la izquierda; datos extraídos, semáforo de auditoría e inspector de JSON a la derecha) sobre React + TypeScript + Tailwind, con arquitectura limpia en el cliente.

## 2. Objetivos

- [ ] Pantalla dividida en dos columnas: `VisorPDF` (izquierda, ~40%) y panel de resultados (derecha, ~60%).
- [ ] Ingesta en 1 click: 3 botones de ejemplos pre-cargados + botón de subida de PDF propio (≤ 5 MB).
- [ ] Semáforo de auditoría: 5 reglas con estado ✅/❌, `codigo_error` y mensaje legible + badge global `APROBADO`/`RECHAZADO`.
- [ ] Desglose de latencia por etapa (IA / reglas / total) visible junto al badge global de estado.
- [ ] Inspector de JSON crudo ("Ver JSON Estructurado (Pydantic)") plegable con copia al portapapeles.
- [ ] Pestaña/panel de **Historial** con auditorías previas (SQLite vía API) y su latencia en ms.
- [ ] Primer render útil < 2 s en local; build TypeScript sin errores.

## 3. Reglas de Negocio y Restricciones

- **RN-4-01:** La UI **no decide** nada de negocio: muestra lo que devuelve la API (estado y reglas). Ninguna regla se re-evalúa ni se recalcula en el cliente.
- **RN-4-02:** Single Page App de **una pantalla** (con panel de historial); sin router de páginas ni store global (React state + hooks).
- **RN-4-03:** Solo se pueden subir archivos `application/pdf` de hasta 5 MB; la validación de tamaño se adelanta en el cliente (feedback inmediato) y se re-confirma en el servidor (RN-3-01).
- **RN-4-04:** El visor de PDF usa la URL servida por la API para ejemplos (`/ejemplos/{id}/pdf`) y blob URLs para archivos subidos; no se copian los PDFs al bundle.
- **RN-4-05:** Estados de UI obligatorios: inicial (vacío con instrucciones), cargando (spinner/botones deshabilitados), resultado, error (mensaje con `codigo` de la API).
- **RN-4-06:** Lenguaje visual: verde = aprobado, rojo = rechazado, gris = pendiente/sin datos; iconografía `lucide-react`.

## 4. Casos de Uso (Given-When-Then)

### CU-01: Auditoría de ejemplo pre-cargado (flujo felíz en 1 click)
- **Given** la app cargada sin auditoría activa
- **When** el operador hace click en el ejemplo "Factura Proveedor Homologado #001"
- **Then** el visor muestra el PDF y, al completarse la auditoría, el panel derecho muestra los datos extraídos, el badge `APROBADO` y las 5 reglas en verde.

### CU-02: Subida de comprobante propio con errores
- **Given** el operador tiene una factura con desvío de monto
- **When** la sube con el botón de carga
- **Then** la UI muestra `RECHAZADO` con la regla R3 en rojo, el `codigo_error` `DISCREPANCIA_CONTABLE` y el mensaje legible con los montos comparados.

### CU-03: Inspección técnica del JSON Pydantic
- **Given** una auditoría completada en pantalla
- **When** el revisor despliega el panel "Ver JSON Estructurado (Pydantic)"
- **Then** visualiza el JSON de la respuesta (datos extraídos + JSON crudo de IA) y puede copiarlo.

### CU-04: Consulta del historial
- **Given** auditorías previas ejecutadas en la sesión o por otros usos locales
- **When** se abre el panel "Historial"
- **Then** se listan con fecha, archivo, estado y `tiempo_ejecucion_ms`; al seleccionar una, se re-carga en el panel principal.

### CU-05: Manejo de errores de la API
- **Given** un PDF escaneado sin texto o un archivo > 5 MB
- **When** la API responde `422`/`413` con error tipado
- **Then** la UI muestra un banner con el `codigo` y `mensaje` sin romper el estado de la pantalla.

## 5. Fuera de Alcance (Out of Scope)

- Login, roles o multi-usuario (sin autenticación en el MVP).
- Modo oscuro/temas personalizables (tema claro único).
- Edición manual de los datos extraídos ("corregir y re-auditar" queda para post-MVP).
- Exportación de resultados (PDF/CSV) y compartición de links a auditorías.
- Test E2E automatizado de la UI (se cubre en MOD-05 con Playwright).
