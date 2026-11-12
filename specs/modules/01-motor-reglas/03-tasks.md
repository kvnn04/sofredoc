# TASKS-01: Dominio y Motor de Reglas — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que las pruebas unitarias sigan pasando.

## Fase 1: Dominio y Puertos (Core)

- [x] **T-01:** Crear `backend/src/domain/models.py` con `ItemFactura`, `FacturaExtraida`, `ReglaResultado` y `ResultadoAuditoria` (incl. `desde_reglas`) según `02-design.md` §2.
- [x] **T-02:** Implementar `backend/src/domain/value_objects/cuit.py` (VO `CUIT` con normalización de guiones, validación de 11 dígitos y dígito verificador Módulo 11).
- [x] **T-03:** Definir puertos: `PadronProveedoresPort` (`buscar(cuit) -> Optional[Proveedor]`) y `ClockPort` (`hoy() -> date`) en `backend/src/domain/ports/`.
- [x] **T-04:** Crear `ContextoAuditoria` y el `Protocol Regla` en `backend/src/domain/rules/base.py`.

## Fase 2: Aplicación y Reglas de Negocio

- [x] **T-05:** Implementar `R1IntegridadCuit` en `backend/src/domain/rules/r1_cuit.py` → `ERROR_CUIT_INVALIDO`.
- [x] **T-06:** Implementar `R2ProveedorHabilitado` en `backend/src/domain/rules/r2_proveedor.py` → `PROVEEDOR_NO_REGISTRADO` (ausente o inactivo).
- [x] **T-07:** Implementar `R3ConsistenciaMatematica` en `backend/src/domain/rules/r3_matematica.py` → `DISCREPANCIA_CONTABLE` (tolerancia ± $1.00, `Decimal`; incluir `detalles` con calculado vs declarado).
- [x] **T-08:** Implementar `R4TopeSinOrdenCompra` en `backend/src/domain/rules/r4_orden_compra.py` → `FALTA_ORDEN_COMPRA` (tope estricto `> 500000`).
- [x] **T-09:** Implementar `R5VigenciaComprobante` en `backend/src/domain/rules/r5_vigencia.py` → `COMPROBANTE_VENCIDO` (futura o > 60 días; hoy − fecha == 60 aprueba).
- [x] **T-10:** Implementar el evaluador `backend/src/domain/rules/engine.py`: **regla de admisión R0** (si `tipo_comprobante="REMITO"` → `REMITO_NO_AUDITABLE`, estado RECHAZADO y se corta el flujo); en caso contrario ejecuta R1→R5 **siempre todas**, arma `ResultadoAuditoria.desde_reglas` y acepta una lista de reglas inyectable (facilita tests).

## Fase 3: Infraestructura (Adaptador de Padrón)

- [x] **T-11:** Crear `backend/data/proveedores.json` con los 4 proveedores de `02-design.md` (3 activos + 1 inactivo).
- [x] **T-12:** Implementar `backend/src/infrastructure/padron/json_padron.py` (`JsonPadronProveedores`) con carga en cache, normalización de CUIT y log de warning si el archivo no existe.
- [x] **T-13:** Implementar `backend/src/infrastructure/clock.py` (`RelojSistema`) que cumple `ClockPort` resolviendo "hoy" con `zoneinfo("America/Argentina/Buenos_Aires")`.

## Fase 4: Tests Unitarios (Pytest)

- [ ] **T-14:** Crear `backend/tests/unit/test_cuit.py`: CUITs válidos de referencia, DV incorrecto, 10 dígitos, letras, formatos con/sin guiones, casos borde dv=0 y dv=10→9.
- [ ] **T-15:** Crear `backend/tests/unit/test_reglas.py` con un fixture factory `factura(**overrides)` sobre una base válida, cubriendo por regla: caso feliz, caso de rechazo, y **casos borde** (verificación en `04-verification.md` §1).
- [ ] **T-16:** Crear `backend/tests/unit/test_engine.py`: estado global APROBADO/RECHAZADO, fallos múltiples simultáneos (CU-06), reglas inyectables parciales.
- [ ] **T-17:** Configurar `pytest-cov` y verificar **100% de cobertura** en `backend/src/domain/` (incluye value_objects y rules); reporte con `--cov-report=term-missing`.
