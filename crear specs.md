# SDD Toolkit — Guía y Plantillas Estándar de Especificaciones

Este kit establece el estándar de **Spec-Driven Development (SDD)** para el proyecto **SofreDoc Validator**. Cada nueva funcionalidad o módulo debe estructurarse en una carpeta dedicada dentro de `specs/` conteniendo los cuatro archivos principales.

---

## Estrategia de Archivos por Módulo

```text
specs/
├── README.md                            # Índice maestro del sistema de especificaciones
└── modules/
    └── [NN-nombre-modulo]/              # Ejemplo: 01-motor-reglas, 02-extraccion-ia
        ├── 01-spec.md                   # Requisitos y Alcance (Visión de Negocio/Producto)
        ├── 02-design.md                 # Diseño Técnico y Arquitectura Limpia
        ├── 03-tasks.md                  # Plan de Ejecución Atómico (IA / Developer Checklist)
        └── 04-verification.md           # Testing, Estrés (k6), E2E (Playwright) y Cierre
```

---

# 1. Plantilla `specs/README.md` (Índice Maestro)

```markdown
# SofreDoc Validator — Especificaciones del Sistema (SDD)

Bienvenido a la fuente única de verdad del proyecto **SofreDoc Validator**. Este directorio contiene las especificaciones técnicas y funcionales estructuradas bajo la metodología **Spec-Driven Development (SDD)**.

## Módulos y Estado

| ID | Módulo / Feature | Estado | Spec | Design | Tasks | Verification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `MOD-00` | Arquitectura Monolito & Core | 🟢 Completado | [01](./modules/00-monolito-core/01-spec.md) | [02](./modules/00-monolito-core/02-design.md) | [03](./modules/00-monolito-core/03-tasks.md) | [04](./modules/00-monolito-core/04-verification.md) |
| `MOD-01` | Dominio y Motor de Reglas | 🟡 En Progreso | [01](./modules/01-motor-reglas/01-spec.md) | [02](./modules/01-motor-reglas/02-design.md) | [03](./modules/01-motor-reglas/03-tasks.md) | [04](./modules/01-motor-reglas/04-verification.md) |
| `MOD-02` | Ingesta PDF y Extracción IA | ⚪ Pendiente | [01](./modules/02-extraccion-ia/01-spec.md) | [02](./modules/02-extraccion-ia/02-design.md) | [03](./modules/03-tasks.md) | [04](./modules/02-extraccion-ia/04-verification.md) |
| `MOD-03` | API REST y SQLite | ⚪ Pendiente | [01](./modules/03-api-sqlite/01-spec.md) | [02](./modules/03-api-sqlite/02-design.md) | [03](./modules/03-api-sqlite/03-tasks.md) | [04](./modules/03-api-sqlite/04-verification.md) |
| `MOD-04` | Frontend Clean Architecture | ⚪ Pendiente | [01](./modules/04-frontend/01-spec.md) | [02](./modules/04-frontend/02-design.md) | [03](./modules/04-frontend/03-tasks.md) | [04](./modules/04-frontend/04-verification.md) |
| `MOD-05` | QA: Playwright & k6 | ⚪ Pendiente | [01](./modules/05-qa-testing/01-spec.md) | [02](./modules/05-qa-testing/02-design.md) | [03](./modules/05-qa-testing/03-tasks.md) | [04](./modules/05-qa-testing/04-verification.md) |

*Leyenda de Estado: ⚪ Pendiente | 🟡 En Progreso | 🟢 Completado | 🔴 Bloqueado*

## Flujo de Trabajo SDD
1. **Definir `01-spec.md`:** Validar el problema de negocio y criterios de aceptación.
2. **Diseñar `02-design.md`:** Congelar la arquitectura limpia, esquemas de datos y contratos.
3. **Planificar `03-tasks.md`:** Desglosar en tareas atómicas marcables (`[ ]`).
4. **Verificar `04-verification.md`:** Validar tests unitarios, integración, k6 y Playwright antes de dar por cerrado.
```

---

# 2. Plantilla `01-spec.md` (Requisitos y Alcance)

```markdown
# SPEC-XX: [Nombre del Módulo / Feature] — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.  
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio
Describir en 1-2 párrafos el punto de dolor o necesidad operativa concreta que resuelve esta especificación.

## 2. Objetivos
- [ ] Objetivo principal medible.
- [ ] Objetivo secundario o beneficio colateral.

## 3. Reglas de Negocio y Restricciones
Enumerar las reglas deterministas o normativas que deben cumplirse sin excepción.
- **RN-01:** Descripción estricta de la regla (ej. CUIT debe validar Algoritmo Módulo 11).
- **RN-02:** Restricción de negocio (ej. comprobantes mayores a $500.000 ARS requieren Orden de Compra).

## 4. Casos de Uso (Given-When-Then)

### CU-01: [Nombre del caso feliz]
- **Given** [Dado un contexto inicial o estado del sistema]
- **When** [Cuando el usuario o sistema ejecuta una acción]
- **Then** [Entonces se espera este resultado específico]

### CU-02: [Nombre del caso de error / desvío]
- **Given** [Dado un contexto inicial]
- **When** [Cuando ocurre un fallo o entrada inválida]
- **Then** [Entonces el sistema responde con el código de error X y estado Y]

## 5. Fuera de Alcance (Out of Scope)
- Elemento 1 no contemplado explícitamente en esta versión.
- Integraciones o características diferidas a fases futuras.
```

---

# 3. Plantilla `02-design.md` (Diseño Técnico)

```markdown
# DESIGN-XX: [Nombre del Módulo / Feature] — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.  
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

Describir la ubicación de cada componente respetando la separación de capas:

```text
backend/src/
├── domain/            # Entidades puras, Value Objects, Interfaces de Puertos
├── application/       # Casos de uso (Use Cases / Services)
├── infrastructure/    # Adaptadores (SQLite, PDF Parser, LLM Client)
└── presentation/      # Endpoints FastAPI, DTOs de Request/Response

frontend/src/
├── domain/            # Modelos e Interfaces TS
├── application/       # Hooks de orquestación / Casos de Uso frontend
├── infrastructure/    # Clientes API (Fetch/Axios)
└── presentation/      # Componentes React + Tailwind
```

## 2. Modelos de Datos y Esferas de Dominio

### Entidades y Value Objects (Python / Pydantic)
```python
# Ejemplo de código del modelo de dominio o Value Object
```

### Esquema de Base de Datos (SQLite)
```sql
-- DDL para la tabla o estructura de persistencia
CREATE TABLE IF NOT EXISTS comprobante_auditoria (
    id TEXT PRIMARY KEY,
    cuit_emisor TEXT NOT NULL,
    monto_total REAL NOT NULL,
    estado_auditoria TEXT NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Contratos de API (HTTP / JSON)

### Endpoint: `POST /api/v1/auditar`
- **Request (multipart/form-data):**
  - `file`: Archivo PDF (máx. 5 MB).
- **Response `200 OK`:**
```json
{
  "id": "aud_123456",
  "estado": "APROBADO",
  "reglas_evaluadas": [
    { "codigo": "R1", "nombre": "Integridad CUIT", "aprobado": true, "mensaje": "OK" }
  ],
  "tiempo_ejecucion_ms": 142
}
```

## 4. Librerías y Dependencias Elegidas
- Backend: `fastapi`, `pydantic`, `pypdf`, `pytest`.
- Frontend: `react`, `typescript`, `tailwindcss`, `lucide-react`.
```

---

# 4. Plantilla `03-tasks.md` (Plan de Ejecución Atómico)

```markdown
# TASKS-XX: [Nombre del Módulo / Feature] — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que las pruebas unitarias sigan pasando.

## Fase 1: Dominio y Puertos (Core)
- [ ] **T-01:** Crear la entidad `Comprobante` y los Value Objects (`CUIT`, `Monto`) en `backend/src/domain/`.
- [ ] **T-02:** Definir la interfaz abstracta `DocumentExtractorPort` en `backend/src/domain/ports/`.

## Fase 2: Aplicación y Reglas de Negocio
- [ ] **T-03:** Programar las 5 reglas en `backend/src/domain/rules/`.
- [ ] **T-04:** Crear el caso de uso `AuditarComprobanteUseCase` en `backend/src/application/`.

## Fase 3: Infraestructura y Presentación
- [ ] **T-05:** Implementar el adaptador de SQLite en `backend/src/infrastructure/db/`.
- [ ] **T-06:** Exponer el endpoint HTTP en `backend/src/presentation/routers/`.

## Fase 4: Frontend (Presentación y Conexión)
- [ ] **T-07:** Crear los componentes visuales en `frontend/src/presentation/`.
- [ ] **T-08:** Conectar el cliente de API para consumir la ruta de auditoría.
```

---

# 5. Plantilla `04-verification.md` (Testing y Cierre)

```markdown
# VERIFICATION-XX: [Nombre del Módulo / Feature] — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)
Comandos para ejecutar las pruebas automatizadas del backend:
```bash
# Correr pruebas de dominio y reglas
pytest backend/tests/unit -v

# Correr pruebas integradas de API y base de datos
pytest backend/tests/integration -v
```

### Cobertura Mínima Requerida
- Domain / Rules Engine: **100%**
- Application / Use Cases: **> 90%**

## 2. Pruebas E2E (Playwright)
Escenarios de interfaz de usuario para garantizar el flujo completo:
```bash
npx playwright test qa/e2e/auditoria.spec.ts
```
- [ ] Verificar la carga de los 3 ejemplos pre-cargados.
- [ ] Confirmar actualización visual del semáforo (`APROBADO` vs `RECHAZADO`).
- [ ] Validar visualización del modal o panel de JSON Pydantic.

## 3. Pruebas de Estrés y Rendimiento (k6)
Ejecutar k6 en modo `EXTRACTOR_MODE=mock` para evaluar concurrencia y la base SQLite sin consumir créditos de IA:

```bash
k6 run qa/load/stress_test.js
```

### Umbrales (SLOs / SLAs)
- **Tasa de error (http_req_failed):** $< 1\%$
- **Latencia p95 (http_req_duration):** $< 500\text{ ms}$
- **Concurrencia objetivo:** $50\text{ usuarios virtuales simultáneos}$

## 4. Registro de Decisiones de Arquitectura (ADR Log)
Documentar desvíos o decisiones de diseño tomadas durante la ejecución:

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| YYYY-MM-DD | Uso de `EXTRACTOR_MODE=mock` | Evitar llamadas al LLM durante pruebas k6. | Pruebas de estrés deterministas y sin costo. |

## 5. Criterio de Aceptación Final (Definition of Done)
- [ ] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [ ] Todos los tests de Pytest pasan en verde.
- [ ] Los tests de Playwright se ejecutan correctamente sin flakiness.
- [ ] k6 cumple con los SLAs de latencia y tasa de error.
```