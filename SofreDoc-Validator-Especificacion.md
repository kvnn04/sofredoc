# SofreDoc Validator — Especificación Técnica de Proyecto (MVP)

**Autor:** Kevin Herrera
**Objetivo:** Prueba de Concepto (PoC) Fullstack & Python/AI diseñada para el equipo de Ingeniería de **Sofre Digital S.A.**  
**Stack Principal:** Python, FastAPI, Pydantic, Structured Outputs (IA), SQLite, React, TypeScript, Tailwind CSS.

---

## 1. Resumen Ejecutivo y Propuesta de Valor

**SofreDoc Validator** es una aplicación web ligera de Procesamiento Inteligente de Documentos (IDP) que automatiza la lectura, estructuración y auditoría de comprobantes comerciales en formato PDF (facturas y remitos).

### ¿Por qué este proyecto destaca frente a Sofre Digital?
1. **Alineación directa con el negocio:** Moderniza una de las verticales históricas de Sofre Digital (gestión documental, digitalización y motores de reglas de negocio) aplicando IA generativa.
2. **Arquitectura híbrida madura (IA + Lógica Determinista):** En lugar de delegar decisiones críticas a un LLM (propenso a errores aritméticos), el sistema utiliza **Structured Outputs** únicamente para transformar texto no estructurado en un esquema tipado de **Pydantic**, delegando las validaciones contables y legales a **código Python puro**.
3. **Evaluación sin fricción (Zero-Setup):** Arquitectura minimalista de una sola pantalla sin dependencias pesadas, con documentos de ejemplo pre-cargados para que cualquier líder técnico o reclutador pueda probar el flujo completo en menos de 15 segundos.

---

## 2. Alcance del Proyecto

### Incluido en el MVP
* **Ingesta flexible:** Subida de archivos PDF (hasta 5 MB) y selector rápido con **3 documentos de ejemplo pre-cargados**.
* **Extracción estructurada:** Lectura de texto del PDF (`pypdf` / `pdfplumber`) y mapeo estricto mediante esquemas Pydantic.
* **Motor de reglas determinista:** Validación automática de **5 reglas de negocio** en Python puro.
* **Interfaz operativa de pantalla dividida:** Visor de documento a la izquierda; tabla de datos extraídos, semáforo de auditoría e inspector de JSON crudo a la derecha.
* **Persistencia ligera:** Registro histórico de auditorías en **SQLite** sin necesidad de servidores de bases de datos externos.
* **Calidad garantizada:** Suite de pruebas unitarias con **Pytest** cubriendo todos los casos borde del motor de reglas.

### Fuera de Alcance (Para mantener simplicidad y foco)
* Gestión de usuarios, autenticación o roles complejos.
* OCR sobre imágenes escaneadas de baja calidad (se enfoca en PDFs digitales estándar).
* Conexión en tiempo real con servicios externos de AFIP/ARCA o ERPs (se simulan padrones locales mediante archivos JSON).

---

## 3. Flujo de Arquitectura

```text
[Usuario: Sube PDF o elige Ejemplo]
               │
               ▼
[Frontend: React + TypeScript (Vite)]
               │  POST /api/v1/auditar (multipart/form-data)
               ▼
[Backend: Python + FastAPI]
   ├── 1. Extractor PDF (pypdf) ──► Texto plano del comprobante
   ├── 2. Agente Extractor (LLM + Pydantic) ──► Objeto JSON tipado (FacturaExtraida)
   ├── 3. Motor de Reglas (Python Puro) ──► Evaluación de 5 condiciones de negocio
   └── 4. Persistencia (SQLite) ──► Guarda resultado y métricas de latencia
               │
               ▼
[Respuesta JSON: Datos + Semáforo de Reglas + Trazabilidad]
```

---

## 4. Casos de Uso Principales

### CU-01: Auditoría de Factura Válida (Flujo Feliz)
* **Actor:** Operador / Analista Administrativo.
* **Acción:** Selecciona el caso pre-cargado *"Factura Proveedor Homologado #001"*.
* **Flujo:** El sistema extrae CUIT, razón social, fecha, número de orden de compra (OC) e ítems. Verifica que el proveedor esté habilitado, que los importes coincidan y aprueba el comprobante.
* **Resultado esperado:** Estado global **APROBADO** con las 5 reglas en verde.

### CU-02: Detección de Inconsistencias Contables o Documentales
* **Actor:** Operador / Analista Administrativo.
* **Acción:** Selecciona *"Factura con Desvío de Monto"* o sube un comprobante propio con errores.
* **Flujo:** La IA extrae los valores literales del documento. El motor en Python detecta que la suma de ítems no coincide con el total o que falta la Orden de Compra obligatoria.
* **Resultado esperado:** Estado global **RECHAZADO**, detallando el código de error exacto y la explicación legible para el usuario.

### CU-03: Inspección Técnica e Historial de Auditorías
* **Actor:** Líder Técnico / Revisor.
* **Acción:** Consulta la pestaña *"Historial"* o despliega el panel *"Ver JSON Estructurado (Pydantic)"*.
* **Resultado esperado:** Visualización de auditorías previas almacenadas en SQLite, tiempo de ejecución en milisegundos y el esquema exacto devuelto por el modelo de IA.

---

## 5. Condiciones y Reglas de Negocio (Motor Determinista)

Todas las validaciones se ejecutan en Python puro sobre el objeto `FacturaExtraida`:

| Código | Regla de Negocio | Condición Técnica Evaluada | Código de Rechazo |
| :--- | :--- | :--- | :--- |
| **R1** | **Integridad de CUIT** | Debe contener 11 dígitos numéricos y superar el algoritmo oficial de dígito verificador (Módulo 11). | `ERROR_CUIT_INVALIDO` |
| **R2** | **Proveedor Habilitado** | El CUIT debe encontrarse activo en el padrón local simulado (`data/proveedores.json`). | `PROVEEDOR_NO_REGISTRADO` |
| **R3** | **Consistencia Matemática** | La suma de `(cantidad * precio_unitario)` + impuestos debe coincidir con `monto_total` (tolerancia ± $1.00). | `DISCREPANCIA_CONTABLE` |
| **R4** | **Tope sin Orden de Compra** | Si `monto_total > $500.000 ARS`, el campo `numero_orden_compra` es obligatorio. | `FALTA_ORDEN_COMPRA` |
| **R5** | **Vigencia del Comprobante** | La fecha de emisión no puede ser futura ni superar los 60 días de antigüedad. | `COMPROBANTE_VENCIDO` |

---

## 6. Estructura del Repositorio

```text
sofredoc-validator/
├── backend/
│   ├── app/
│   │   ├── main.py           # Endpoints FastAPI (/auditar, /historial, /ejemplos)
│   │   ├── schemas.py        # Modelos Pydantic (FacturaExtraida, ResultadoAuditoria)
│   │   ├── extractor.py      # Lectura de PDF y llamada Structured Output a la IA
│   │   ├── rules_engine.py   # Implementación pura de las 5 reglas de negocio
│   │   └── database.py       # Gestión ligera de SQLite
│   ├── tests/
│   │   └── test_rules.py     # Pruebas unitarias con Pytest para las 5 reglas
│   ├── data/
│   │   ├── proveedores.json  # Padrón simulado de proveedores habilitados
│   │   └── ejemplos/         # 3 archivos PDF listos para demostración
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # VisorPDF, TablaDatos, SemaforoReglas, Historial
│   │   └── App.tsx           # Interfaz principal de dos columnas
│   └── package.json
└── README.md                 # Documentación visual, arquitectura y guía de ejecución
```

---

## 7. Plan de Ejecución (4 Días)

* **Día 1 — Núcleo Backend y Reglas:** Crear entorno Python, definir `schemas.py`, programar las 5 funciones en `rules_engine.py` y escribir los tests en `test_rules.py`.
* **Día 2 — Extracción IA y API:** Implementar `extractor.py` con Structured Outputs, conectar `SQLite` y exponer los endpoints en FastAPI.
* **Día 3 — Frontend React/TypeScript:** Construir la pantalla dividida en dos columnas con Tailwind CSS, botones de carga rápida y visualización del semáforo de reglas.
* **Día 4 — Pulido y Despliegue:** Generar los 3 PDFs de ejemplo, redactar un `README.md` impecable con capturas y desplegar en la nube (Vercel + Render/Railway).
