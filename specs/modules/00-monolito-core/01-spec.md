# SPEC-00: Arquitectura Monolito & Core — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio

SofreDoc Validator es una PoC fullstack que debe poder evaluarse por líderes técnicos y reclutadores en **menos de 15 segundos** de setup. Si el esqueleto del repositorio (estructura, configuración, arranque de servicios) no está estandarizado desde el inicio, cada módulo posterior introduce su propia convención, el onboarding se encarece y la demo pierde la promesa de "zero-setup".

Este módulo establece el **esqueleto monolítico con Clean Architecture** (FastAPI + React) y las convenciones base que el resto de los módulos reutilizan.

## 2. Objetivos

- [ ] Repositorio monorepo (`backend/` + `frontend/` + `qa/` + `specs/`) arrancable con dos comandos: `uvicorn` y `npm run dev`.
- [ ] Endpoint de salud `GET /api/v1/health` operativo para verificar el backend en 1 segundo.
- [ ] Configuración por variables de entorno (`.env.example` versionado) sin secretos en el código.
- [ ] Frontend Vite + React + TypeScript + Tailwind compila y renderiza la pantalla base vacía.

## 3. Reglas de Negocio y Restricciones

- **RN-00-01:** Arquitectura monolítica: **un solo proceso backend** (FastAPI) y **un solo proceso frontend** (Vite). Prohibidos microservicios, colas y servidores de bases de datos externos (SQLite en archivo).
- **RN-00-02:** Clean Architecture obligatoria: el dominio (`domain/`) **no puede importar** FastAPI, SQLite, `pypdf` ni SDKs de LLM. Toda I/O vive en `infrastructure/`.
- **RN-00-03:** Sin autenticación ni gestión de usuarios (explícitamente fuera de alcance del MVP).
- **RN-00-04:** Versiones base: **Python ≥ 3.11**, **Node ≥ 20**.
- **RN-00-05:** Toda configuración externa (modo extractor, credenciales LLM, rutas de datos) se lee de variables de entorno, nunca hardcodeada.

## 4. Casos de Uso (Given-When-Then)

### CU-01: Arranque del stack de desarrollo
- **Given** un evaluador con Python 3.11+ y Node 20+ instalados
- **When** ejecuta los comandos del quickstart (backend y frontend en dos terminales)
- **Then** el backend responde en `http://localhost:8000` y el frontend en `http://localhost:5173` sin errores en consola.

### CU-02: Verificación de salud del servicio
- **Given** el backend corriendo
- **When** se solicita `GET /api/v1/health`
- **Then** responde `200` con `{"status": "ok", ...}` indicando versión y `EXTRACTOR_MODE` activo.

### CU-03: Cambio de configuración sin tocar código
- **Given** un desarrollador quiere correr la demo sin créditos de IA
- **When** define `EXTRACTOR_MODE=mock` en su `.env`
- **Then** el arranque del sistema refleja el modo seleccionado en `/api/v1/health` y ningún módulo necesita modificación.

## 5. Fuera de Alcance (Out of Scope)

- Docker / docker-compose para orquestación (se valora como mejora posterior).
- CI/CD pipelines (se abordan en MOD-05 solo como verificación local + workflow opcional).
- Autenticación, autorización, roles o multi-tenancy.
- Despliegue a la nube (Vercel + Render/Railway se ejecuta en el Día 4 del plan, fuera de las specs de código).
