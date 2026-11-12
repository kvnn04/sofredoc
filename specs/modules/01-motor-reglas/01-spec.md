# SPEC-01: Dominio y Motor de Reglas — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio

La auditoría manual de comprobantes (facturas y remitos) es lenta, propensa a error humano y difícil de auditar: verificar un CUIT a mano, recalcular sumas de ítems o comprobar vigencias toma minutos por documento y produce inconsistencias entre operadores.

Este módulo implementa el **motor de reglas determinista en Python puro** que audita un comprobante estructurado (`FacturaExtraida`) en milisegundos, con códigos de error exactos y mensajes legibles. Es el núcleo de valor del proyecto: **las decisiones contables y legales nunca las toma la IA**, sino este código verificable.

## 2. Objetivos

- [ ] Implementar las **5 reglas de negocio (R1–R5)** como funciones/clases puras, sin I/O ni frameworks.
- [ ] Cobertura de tests del dominio y reglas: **100%**.
- [ ] Cada rechazo reporta `codigo_error` estable + `mensaje` legible para el operador.
- [ ] La evaluación de las 5 reglas corre en **< 10 ms** (sin I/O en el camino caliente).

## 3. Reglas de Negocio y Restricciones

- **RN-01 (Integridad de CUIT):** el CUIT debe tener 11 dígitos numéricos (acepta formato `3012345678_1`, `30-12345678-1` y `30123456781`, que se normalizan) y superar el algoritmo oficial de dígito verificador **Módulo 11**. Código de rechazo: `ERROR_CUIT_INVALIDO`.
- **RN-02 (Proveedor Habilitado):** el CUIT normalizado debe existir **y estar activo** en el padrón local simulado (`backend/data/proveedores.json`). Código de rechazo: `PROVEEDOR_NO_REGISTRADO` (aplica tanto a CUIT ausente como inactivo).
- **RN-03 (Consistencia Matemática):** `Σ(cantidad × precio_unitario) + impuestos` debe coincidir con `monto_total` con **tolerancia ± $1.00 ARS**. Código de rechazo: `DISCREPANCIA_CONTABLE`.
- **RN-04 (Tope sin Orden de Compra):** si `monto_total > $500.000 ARS`, el campo `numero_orden_compra` es obligatorio (no nulo y no vacío). Con `monto_total == 500.000` exacto **no** se exige OC (la regla es estrictamente mayor). Código de rechazo: `FALTA_ORDEN_COMPRA`.
- **RN-05 (Vigencia del Comprobante):** `fecha_emision` no puede ser futura ni superar los **60 días** de antigüedad. Emitida hoy = válida; a exactamente 60 días = válida; a 61 días = vencida. Código de rechazo: `COMPROBANTE_VENCIDO`.
- **RN-06 (Estado global):** `APROBADO` solo si las 5 reglas pasan; cualquier fallo produce `RECHAZADO` con el detalle de **todas** las reglas fallidas (nunca se corta en la primera).
- **RN-07 (Determinismo):** ninguna regla consulta servicios externos ni depende de la red; el "hoy" se inyecta (Clock) para hacer la evaluación testeable y se resuelve en la zona horaria `America/Argentina/Buenos_Aires` (decisión 2026-11-12).
- **RN-08 (Admisión de comprobantes — R0):** en el MVP solo se auditan `FACTURA`s. Si el comprobante extraído es `REMITO`, la regla de admisión R0 lo rechaza con `REMITO_NO_AUDITABLE` **sin evaluar R1–R5** (sin importes no hay matemática ni tope de OC que auditar).

## 4. Casos de Uso (Given-When-Then)

### CU-01: Factura completamente válida (flujo feliz)
- **Given** una `FacturaExtraida` con CUIT válido y registrado/activo, montos consistentes, sin tope excedido y fecha reciente
- **When** el motor de reglas la evalúa
- **Then** las 5 reglas devuelven `aprobado=true` y el estado global es `APROBADO`.

### CU-02: Desvío de monto contable
- **Given** una factura cuya suma de ítems + impuestos difiere del `monto_total` en más de $1.00
- **When** el motor evalúa R3
- **Then** R3 marca `aprobado=false` con `codigo_error=DISCREPANCIA_CONTABLE` y un mensaje que muestra ambos montos; el estado global es `RECHAZADO`.

### CU-03: Monto alto sin Orden de Compra
- **Given** una factura de `monto_total` $725.000 sin `numero_orden_compra`
- **When** el motor evalúa R4
- **Then** R4 marca `aprobado=false` con `codigo_error=FALTA_ORDEN_COMPRA`; con una OC cargada la misma factura aprueba R4.

### CU-04: CUIT inválido o proveedor no registrado
- **Given** una factura con CUIT de dígito verificador incorrecto, **o** con CUIT válido pero ausente/inactivo en el padrón
- **When** el motor evalúa R1 y R2
- **Then** R1 rechaza con `ERROR_CUIT_INVALIDO` (primer caso) y R2 rechaza con `PROVEEDOR_NO_REGISTRADO` (segundo caso).

### CU-05: Comprobante vencido o futuro
- **Given** una factura emitida a 61 días o más, **o** con fecha futura
- **When** el motor evalúa R5
- **Then** R5 rechaza con `COMPROBANTE_VENCIDO`, distinguiendo en el mensaje si la fecha es futura o vencida.

### CU-06: Fallos múltiples simultáneos
- **Given** una factura que incumple R3 y R5 a la vez
- **When** el motor la evalúa
- **Then** se reportan **ambos** fallos y las demás reglas igual se ejecutan y reportan su estado.

### CU-07: Remito fuera de alcance (decisión 2026-11-12)
- **Given** un comprobante extraído como `tipo_comprobante="REMITO"`
- **When** el motor lo evalúa
- **Then** la regla de admisión R0 lo rechaza con `REMITO_NO_AUDITABLE`, el estado global es `RECHAZADO` y las reglas R1–R5 **no se evalúan** (el semáforo muestra solo la fila R0).

## 5. Fuera de Alcance (Out of Scope)

- Consulta online a AFIP/ARCA (el padrón es un JSON local simulado).
- OCR o corrección heurística de CUITs ilegibles (eso es responsabilidad de la extracción, MOD-02).
- Conversión de moneda, retenciones avanzadas, percepciones por jurisdicción o IVA por alícuota.
- Remitos con items sin precios (se asume comprobante con importes).
