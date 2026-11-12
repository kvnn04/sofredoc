# PROGRESO.md — Bitácora de Continuidad del Proyecto

> **Para todo agente de IA:** este archivo es tu punto de partida junto con `AGENTS.md`. Describe el estado **exacto** del proyecto. Al cerrar tu sesión, agregá una entrada nueva al final usando la plantilla de abajo. No edites ni borres entradas anteriores (el historial es trazabilidad).

---

## Estado actual (resumen rápido)

- **Fase del proyecto:** Especificación completa (v2, refinada) — **implementación no iniciada**.
- **Siguiente acción concreta:** `MOD-00` → Fase 1 → tarea **T-00** (git init + `.gitignore` + primer commit "specs SDD v1") y T-01 (estructura de carpetas).
- **Módulos:** 00 ⚪ Pendiente · 01 ⚪ Pendiente · 02 ⚪ Pendiente · 03 ⚪ Pendiente · 04 ⚪ Pendiente · 05 ⚪ Pendiente.
- **Bloqueos:** ninguno.
- **Configuración del usuario (Kevin):** autonomía completa (tests, deps, archivos, commit local, LLM real, push/deploy) · verificación completa obligatoria · desvío menor → ADR y seguir; desvío de contrato/esquema/regla → preguntar · commits por fase.
- **Protocolo de sesión (misión implícita en AGENTS.md §3):** Kevin escribe una palabra y el agente ya sabe qué hacer — `arrancá` = módulo pendiente completo (anuncia y ejecuta, sin esperar confirmación) · `MOD-XX` / `MOD-XX Fase N` = override · `prueba` = solo próxima fase · `estado` = resumen · `todo` = continuo hasta el final · `DoD` = revisión final. Al cerrar un módulo: bitácora + estado 🟢 en specs/README.md + **esperar al usuario** (no continuar al siguiente módulo por su cuenta).

---

## Plantilla de entrada (copiar, completar y pegar al final)

```markdown
## [YYYY-MM-DD] Sesión — MOD-XX / Fase N

**Qué se hizo:**
- (tareas T-XX completadas, marcadas [x] en 03-tasks.md)

**Verificación ejecutada (evidencia real):**
- (ej.: pytest backend/tests/unit -v → 24 passed; npm run build → ok; ruff → sin hallazgos)

**Archivos creados/modificados clave:**
- (lista breve)

**Decisiones / ADRs nuevos (si los hay):**
- (desvíos registrados en 04-verification.md del módulo, con motivo)

**Estado exacto al cerrar:**
- (ej.: MOD-00 T-01..T-04 ✓; T-05..T-07 ✗ — frontend sin scaffold)

**Próximos pasos para la próxima sesión:**
1. (acción más urgente y concreta)
2. (…)

**Costo LLM real (si hubo llamadas en modo llm):**
- (ej.: 3 llamadas gpt-4o-mini, ~2.1k tokens entrada — USD ~0.001)
```

---

## Historial de sesiones

### [2026-11-12] Sesión 0 — Especificación SDD completa (v2)

**Qué se hizo:**
- Creadas las specs SDD completas: `specs/README.md` + 6 módulos × 4 archivos (25 documentos).
- Sesión de refinamiento con Kevin (15 preguntas): decisiones aplicadas y specs actualizadas.

**Decisiones firmes (registradas en ADRs de cada módulo):**
- Proveedor IA: OpenAI `gpt-4o-mini` (Structured Outputs, temp 0, 1 reintento).
- Solo facturas auditable: regla de admisión R0 (`REMITO_NO_AUDITABLE`) sin evaluar R1–R5.
- CUIT Módulo 11: dv=11→0, dv=10→9. Tolerancia R3 ±$1.00; tope R4 estricto >$500.000; R5 0–60 días con reloj `America/Argentina/Buenos_Aires`.
- PDFs ≤5 MB y ≤10 páginas; campos críticos faltantes → `EXTRACCION_FALLIDA`; `RECHAZADO` es `200 OK`.
- Latencia desglosada por etapa (`latencia_extraccion_ms`, `latencia_reglas_ms`, total).
- Deploy de cierre: Render + Vercel (SQLite efímero aceptado). Git: commit por módulo/fase.

**Estado exacto al cerrar:**
- Specs 100% listas y consistentes. Implementación 0%.

**Próximos pasos:**
1. `MOD-00` Fase 1: T-00 (git init + .gitignore + commit "specs SDD v1"), T-01 estructura de carpetas, T-02 venv + requirements.txt, T-03 config.py + .env.example, T-04 main.py + /health.
2. Continuar Fases 2–3 del MOD-00 (scaffold frontend + calidad base) y seguir el orden MOD-00→05.
