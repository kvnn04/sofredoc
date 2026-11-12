# VERIFICATION-03: API REST y SQLite — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Correr pruebas integradas de API y base de datos
pytest backend/tests/integration -v

# Suite completo del backend (unit + integration)
pytest backend/tests -v --cov=src --cov-report=term-missing
```

### Cobertura Mínima Requerida
- Application / Use Cases (`AuditarComprobanteUseCase`): **> 90%**
- Infrastructure/db (repositorio SQLite): **> 90%**
- Presentation/routers: cubiertos por los tests de integración (flujos felices + errores tipados).

### Matriz de Verificación de Integración

| # | Escenario | Request | Esperado |
| :--- | :--- | :--- | :--- |
| 1 | Flujo feliz (ejemplo aprobado) | POST con `ej-factura-aprobada` (bytes) | 200, `estado=APROBADO`, 5 reglas `aprobado=true`, `id` con formato `aud_*`, fila persistida |
| 2 | Desvío contable | POST con `ej-factura-desvio` | 200, `estado=RECHAZADO`, R3 con `DISCREPANCIA_CONTABLE` y mensaje con montos |
| 3 | Tope sin OC | POST con `ej-monto-alto-sin-oc` | 200, `estado=RECHAZADO`, R4 con `FALTA_ORDEN_COMPRA` |
| 4 | Archivo > 5 MB | POST con blob de 6 MB | 413 `ARCHIVO_MUY_GRANDE` |
| 5 | No-PDF | POST con `archivo.txt` | 422 `PDF_INVALIDO` |
| 6 | PDF sin texto | POST con PDF de imagen | 422 `PDF_SIN_TEXTO` |
| 7 | Extracción fallida | extractor stub que siempre falla | 502 `EXTRACCION_FALLIDA` |
| 8 | Historial paginado | GET `/historial?limit=2&offset=0` tras 3 auditorías | 200, 2 ítems, orden descendente por `creado_en` |
| 9 | Detalle | GET `/historial/{id}` | 200 con `json_crudo_ia`; GET id inexistente → 404 `AUDITORIA_NO_ENCONTRADA` |
| 10 | Ejemplos | GET `/ejemplos` + `/ejemplos/{id}/pdf` | 200 con 3 ítems y PDF `application/pdf` > 0 bytes |
| 11 | Multi-página | POST con PDF de 11 páginas (fixture) | 422 `PDF_INVALIDO` con mensaje de límite de páginas |

## 2. Pruebas E2E (Playwright)

Cubiertas en MOD-05 sobre esta API ya desplegada localmente.

## 3. Pruebas de Estrés y Rendimiento (k6)

Cubiertas en MOD-05 (con `EXTRACTOR_MODE=mock` esta API sostiene 50 VUs con p95 < 500 ms objetivo).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `RECHAZADO` responde `200 OK` | El rechazo es un **resultado de negocio** válido; 4xx/5xx reservados a fallos de contrato/infra. | La UI distingue estado del semáforo, no códigos HTTP, para el semáforo. |
| 2026-11-12 | Estado `ERROR_EXTRACCION` solo en tabla | Trazabilidad de fallos sin contaminar el semáforo de reglas. | `reglas_evaluadas=[]` en ese estado. |
| 2026-11-12 | SQLite WAL + `check_same_thread=False` | PoC mono-proceso con concurrencia moderada (k6 50 VUs de solo lectura + escrituras acotadas). | Tope práctico de escrituras concurrentes; suficiente para MVP. |
| 2026-11-12 | PDFs de ejemplo generados por script con fechas relativas | Los ejemplos deben permanecer vigentes (R5: 60 días) sin regeneración manual periódica. | Re-ejecutar `generar_ejemplos.py` si la demo envejece > 60 días. |
| 2026-11-12 | Montos `Decimal` → REAL + JSON numérico 2 decimales | Precisión en dominio; legibilidad en UI. | Conversión explícita en DTOs. |
| 2026-11-12 | Latencia desglosada por etapa (IA / reglas) | Confirmado por el product owner: hace visible la arquitectura híbrida ante el evaluador técnico. | 2 columnas nuevas en SQLite + campos en DTO y UI. |
| 2026-11-12 | SQLite efímero en deploy (free tier) | Render reinicia el disco en cada deploy; el historial es volátil en producción gratuita. | Nota obligatoria en README y smoke post-deploy (MOD-05 §5). |

## 5. Criterio de Aceptación Final (Definition of Done)

- [ ] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [ ] Todos los tests de integración pasan en verde contra SQLite temporal (sin tocar `data/sofredoc.db` real).
- [ ] Los 10 escenarios de la matriz §1 verificados.
- [ ] Los 3 PDFs de ejemplo existen y los endpoints `/ejemplos` y `/ejemplos/{id}/pdf` los sirven.
- [ ] `curl` manual de la matriz de contratos reproduce las respuestas de `02-design.md` §3.
- [ ] Un flujo completo manual (mock mode) audita un PDF en < 2 s end-to-end.
