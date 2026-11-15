# Despliegue de cierre — Render (backend) + Vercel (frontend) — MOD-05 Fase 5

> **Estado:** ✅ **Ejecutado 2026-11-15** — producción en https://sofredoc.vercel.app (Vercel) +
> https://sofredoc-api.onrender.com (Render). Smoke post-deploy en verde (matriz de verdad,
> semáforo, JSON inspector e historial); ambos modos (`mock`/`llm`) verificados — quedó `mock`
> para la demo diaria (conmutar en Render al enviar a evaluación, §5).
> Confirma la decisión de `04-verification.md` §4: SQLite efímero en el free tier de
> Render — **el historial se reinicia en cada deploy** (aceptado y documentado).

## 0. Prerrequisitos

1. Repo publicado en GitHub — remote `origin` ya configurado (`https://github.com/kvnn04/sofredoc.git`):
   ```powershell
   git push -u origin main
   ```
2. Cuentas en [render.com](https://render.com) y [vercel.com](https://vercel.com) (plan free).

## 1. Backend en Render

Opción A — **Blueprint (recomendada):** en Render → *New → Blueprint*, elegir el repo;
lee `render.yaml` (en la raíz) y crea el servicio `sofredoc-api`.

Opción B — manual: *New → Web Service* con:

| Campo | Valor |
| :--- | :--- |
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

Variables de entorno (→ *Environment*):

| Variable | Valor | Nota |
| :--- | :--- | :--- |
| `EXTRACTOR_MODE` | `mock` | Para el smoke post-deploy sin costo. Cambiar a `llm` después si se carga `LLM_API_KEY`. |
| `LLM_PROVIDER` / `LLM_MODEL` | `openai` / `gpt-4o-mini` | Solo si se usa modo `llm`. |
| `LLM_API_KEY` | *(vacía)* | Setear en el dashboard (nunca en el repo). Solo para modo `llm`. |
| `CORS_ORIGINS` | `https://<proyecto>.vercel.app` | Completar **después** del paso 2 y volver a hacer deploy. |

Verificación: `GET https://<backend>.onrender.com/api/v1/health` → `{"status":"ok",...}`.

## 2. Frontend en Vercel

1. *Add New → Project* → importar el repo.
2. **Root Directory:** `frontend` (Vite se auto-detecta).
3. Variables de entorno: `VITE_API_URL=https://<backend>.onrender.com/api/v1`
   (el backend de Render, **con** `/api/v1` incluido).
4. Deploy. Anotar el dominio final (ej. `https://sofredoc.vercel.app`).

## 3. Cerrar el círculo CORS

En Render → `sofredoc-api` → *Environment*: `CORS_ORIGINS=https://<dominio-final>.vercel.app`
→ *Save* → Render redespliega. (Sin esto, el navegador bloquea las llamadas desde Vercel.)

## 4. Smoke post-deploy (T-16)

```powershell
# 1) Health del backend público
curl https://<backend>.onrender.com/api/v1/health

# 2) Auditoría del ejemplo #001 (modo mock → APROBADO)
curl.exe -s -X POST https://<backend>.onrender.com/api/v1/auditar `
  -F "file=@backend/data/ejemplos/factura-aprobada-001.pdf;type=application/pdf"

# 3) (opcional) Remito → RECHAZADO por admisión R0 (REMITO_NO_AUDITABLE, 1 sola regla)
curl.exe -s -X POST https://<backend>.onrender.com/api/v1/auditar `
  -F "file=@qa/e2e/fixtures/remito-transporte-2026.pdf;type=application/pdf"

# 4) UI: abrir https://<dominio>.vercel.app, clic en cada ejemplo y confirmar
#    APROBADO / RECHAZADO-R3 / RECHAZADO-R4, JSON inspector e historial.
```

Marcar como hechos: T-14, T-15, T-16 de `03-tasks.md` + los 3 ítems pendientes del
DoD §5 (`04-verification.md`), y el estado de MOD-05 a 🟢 en `specs/README.md`.

## 5. Notas operativas

- **SQLite efímero:** el free tier de Render reinicia el disco en cada deploy → el
  historial arranca vacío (documentado y aceptado; persistencia real = disco persistente
  o Postgres, fuera de alcance del MVP).
- **Cold start del free tier:** tras ~15 min sin tráfico, el primer request tarda ~30–60 s
  (el servicio se "despierta"). Considerar en la demo en vivo.
- **Vigencia de la demo:** los PDFs de ejemplo y las fixtures del mock llevan fechas
  relativas a su generación (hoy−5/−20/−30 y estáticas). Si la demo envejece >60 días (R5),
  regenerar: `cd backend ; python scripts/generar_ejemplos.py` (+ refrescar fixtures si
  corresponde — ver ADR-02-06 y ADR-05-01).
- **Modo `llm`:** cambiar `EXTRACTOR_MODE=llm` + `LLM_API_KEY` en Render; registrar cada
  tramo de prueba con LLM real en `specs/PROGRESO.md` (control de costo).
