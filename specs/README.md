# SofreDoc Validator — Especificaciones del Sistema (SDD)

Bienvenido a la **fuente única de verdad** del proyecto **SofreDoc Validator**. Este directorio contiene las especificaciones técnicas y funcionales estructuradas bajo la metodología **Spec-Driven Development (SDD)**.

> **Documentos de origen:**
> - `SofreDoc-Validator-Especificacion.md` — Especificación Técnica del MVP (autor: Kevin Herrera).
> - `crear specs.md` — Toolkit de plantillas SDD.

## Módulos y Estado

| ID | Módulo / Feature | Estado | Spec | Design | Tasks | Verification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `MOD-00` | Arquitectura Monolito & Core | 🟢 Completado | [01](./modules/00-monolito-core/01-spec.md) | [02](./modules/00-monolito-core/02-design.md) | [03](./modules/00-monolito-core/03-tasks.md) | [04](./modules/00-monolito-core/04-verification.md) |
| `MOD-01` | Dominio y Motor de Reglas | 🟢 Completado | [01](./modules/01-motor-reglas/01-spec.md) | [02](./modules/01-motor-reglas/02-design.md) | [03](./modules/01-motor-reglas/03-tasks.md) | [04](./modules/01-motor-reglas/04-verification.md) |
| `MOD-02` | Ingesta PDF y Extracción IA | 🟢 Completado | [01](./modules/02-extraccion-ia/01-spec.md) | [02](./modules/02-extraccion-ia/02-design.md) | [03](./modules/02-extraccion-ia/03-tasks.md) | [04](./modules/02-extraccion-ia/04-verification.md) |
| `MOD-03` | API REST y SQLite | 🟢 Completado | [01](./modules/03-api-sqlite/01-spec.md) | [02](./modules/03-api-sqlite/02-design.md) | [03](./modules/03-api-sqlite/03-tasks.md) | [04](./modules/03-api-sqlite/04-verification.md) |
| `MOD-04` | Frontend Clean Architecture | 🟢 Completado | [01](./modules/04-frontend/01-spec.md) | [02](./modules/04-frontend/02-design.md) | [03](./modules/04-frontend/03-tasks.md) | [04](./modules/04-frontend/04-verification.md) |
| `MOD-05` | QA: Pytest, Playwright & k6 | 🟡 En Progreso *(QA completo: pytest 129 + E2E 10 escenarios + k6 saturación y funcional; falta deploy de cierre T-14..T-16)* | [01](./modules/05-qa-testing/01-spec.md) | [02](./modules/05-qa-testing/02-design.md) | [03](./modules/05-qa-testing/03-tasks.md) | [04](./modules/05-qa-testing/04-verification.md) |

*Leyenda de Estado: ⚪ Pendiente | 🟡 En Progreso | 🟢 Completado | 🔴 Bloqueado*

## Orden de Ejecución (dependencias)

```text
MOD-00 → MOD-01 → MOD-02 → MOD-03 → MOD-04 → MOD-05
```

Cada módulo depende del anterior: el core define el esqueleto, el dominio define las reglas puras, la extracción produce los datos que las reglas consumen, la API orquesta y persiste, el frontend consume la API y el QA valida el conjunto.

## Flujo de Trabajo SDD

1. **Definir `01-spec.md`:** Validar el problema de negocio y criterios de aceptación.
2. **Diseñar `02-design.md`:** Congelar la arquitectura limpia, esquemas de datos y contratos.
3. **Planificar `03-tasks.md`:** Desglosar en tareas atómicas marcables (`[ ]`).
4. **Verificar `04-verification.md`:** Validar tests unitarios, integración, k6 y Playwright antes de dar por cerrado.

## Convenciones Globales

Aplican a todos los módulos y su incumplimiento debe registrarse en el ADR Log de `04-verification.md`:

- **Idioma:** español para documentación, mensajes de usuario y nombres de negocio; código en inglés salvo conceptos de negocio (ej. `FacturaExtraida`, `numero_orden_compra`).
- **Moneda:** ARS. El dominio trabaja con `Decimal`; la serialización JSON expone montos numéricos con 2 decimales.
- **Fechas:** ISO 8601 (`YYYY-MM-DD` para fechas de comprobante; `YYYY-MM-DDTHH:MM:SSZ` para timestamps UTC).
- **IDs de auditoría:** `aud_` + 8 caracteres hexadecimales (ej. `aud_9f2c1a7b`).
- **API base:** `/api/v1`. Backend en `:8000`, Frontend en `:5173`.
- **Códigos de error:** `MAYUSCULAS_CON_GUIONES_BAJOS`, sin prefijos HTTP.
- **Arquitectura:** Clean Architecture (monolito FastAPI + React). Toda I/O (SQLite, PDF, LLM, padrón JSON) vive en `infrastructure/`; el dominio es Python puro sin imports de framework.
- **Configuración:** variables de entorno vía `pydantic-settings`, documentadas en `.env.example`.
- **Alcance de comprobantes:** solo `FACTURA` es auditable en el MVP; un `REMITO` se rechaza por la regla de admisión R0 (`REMITO_NO_AUDITABLE`) sin evaluar R1–R5 (decisión 2026-11-12).
- **Extracción:** proveedor fijado **OpenAI `gpt-4o-mini`** con Structured Outputs (ADR en MOD-02); `EXTRACTOR_MODE=mock` por default. Máximo **10 páginas** por comprobante.
- **Métricas:** latencia desglosada por etapa (`latencia_extraccion_ms` IA, `latencia_reglas_ms` reglas) además del tiempo total.
- **Zona horaria:** el reloj del sistema (R5) resuelve "hoy" en `America/Argentina/Buenos_Aires`.
- **Deploy:** backend en **Render** + frontend en **Vercel** como cierre del MOD-05; SQLite efímero en free tier (el historial se reinicia en cada deploy).
- **Control de versiones:** git con **un commit por módulo/fase** (T-00 del MOD-00).

## Mapa de Correspondencia con el Documento Original

| Archivo original (`backend/app/`) | Destino Clean Architecture |
| :--- | :--- |
| `schemas.py` | `domain/models.py` + `presentation/dtos.py` |
| `rules_engine.py` | `domain/rules/` |
| `extractor.py` | `infrastructure/pdf/` + `infrastructure/llm/` |
| `database.py` | `infrastructure/db/` |
| `main.py` | `main.py` (app factory) + `presentation/routers/` |
