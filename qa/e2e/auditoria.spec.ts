/**
 * E2E del flujo de auditoría (DESIGN-05 §3, CU-02, RN-5-04).
 *
 * Los 4 escenarios obligatorios usan los 3 ejemplos pre-cargados (resultados
 * esperados conocidos: APROBADO / RECHAZADO-R3 / RECHAZADO-R4) y cierran con
 * el JSON inspector + historial. Van en `serial` porque el historial acumula
 * las auditorías previas sobre la BD efímera del backend (ver playwright.config.ts).
 *
 * Con `CAPTURAS=1` cada escenario guarda una captura en `docs/capturas/`
 * (para el README); en CI y corridas normales no escribe nada.
 */
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test, type Page } from "@playwright/test";

const SEMAFORO = "Semáforo de auditoría";
const CODIGOS_ERROR =
  /ERROR_CUIT_INVALIDO|PROVEEDOR_NO_REGISTRADO|DISCREPANCIA_CONTABLE|FALTA_ORDEN_COMPRA|COMPROBANTE_VENCIDO|REMITO_NO_AUDITABLE/;

function ejemplo(nombre: string) {
  return `Auditar ejemplo: ${nombre}`;
}

/** Captura para el README (solo con CAPTURAS=1; RN-5-05: sin artefactos en corridas normales). */
async function captura(page: Page, nombre: string): Promise<void> {
  if (process.env.CAPTURAS !== "1") return;
  const destino = resolve(process.cwd(), "docs", "capturas");
  mkdirSync(destino, { recursive: true });
  await page.screenshot({ path: resolve(destino, nombre), fullPage: true });
}

test.describe.serial("Flujo de auditoría (demo con 3 ejemplos)", () => {
  test("1) ejemplo aprobado → badge APROBADO + 5 reglas ✅ + latencias", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: ejemplo("Factura Proveedor Homologado #001") }).click();

    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("APROBADO", { exact: true })).toBeVisible();
    // Las 5 reglas se evalúan siempre (sin cortocircuito): 5 filas, ninguna con error.
    await expect(semaforo.getByRole("listitem")).toHaveCount(5);
    await expect(semaforo.getByText(CODIGOS_ERROR)).toHaveCount(0);
    // Desglose de latencia por etapa junto al badge (convención global).
    await expect(semaforo.getByText(/IA \d+ ms · reglas \d+ ms · .*total \d+ ms/)).toBeVisible();
    // El id de auditoría respeta la convención `aud_` + 8 hex.
    await expect(semaforo.getByText(/^aud_[0-9a-f]{8}$/)).toBeVisible();

    await captura(page, "demo-01-aprobado.png");
  });

  test("2) ejemplo con desvío → RECHAZADO por R3 (DISCREPANCIA_CONTABLE)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: ejemplo("Factura con desvío de monto") }).click();

    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("RECHAZADO", { exact: true })).toBeVisible();
    await expect(semaforo.getByText("DISCREPANCIA_CONTABLE")).toBeVisible();
    // El resto del semáforo sigue en verde: 5 reglas evaluadas.
    await expect(semaforo.getByRole("listitem")).toHaveCount(5);

    await captura(page, "demo-02-rechazado.png");
  });

  test("3) ejemplo monto alto sin OC → RECHAZADO por R4 (FALTA_ORDEN_COMPRA)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: ejemplo("Factura monto alto sin OC") }).click();

    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("RECHAZADO", { exact: true })).toBeVisible();
    await expect(semaforo.getByText("FALTA_ORDEN_COMPRA")).toBeVisible();
    await expect(semaforo.getByRole("listitem")).toHaveCount(5);
    await expect(semaforo.getByText("DISCREPANCIA_CONTABLE")).toHaveCount(0); // solo R4 falla
  });

  test("4) JSON inspector (Pydantic + crudo IA) e historial con latencias", async ({ page }) => {
    await page.goto("/");

    // Historial: ≥ 3 filas tras los 3 escenarios, con latencia en ms.
    await page.getByRole("button", { name: /Historial de auditorías/ }).click();
    const filas = page.getByLabel(/Ver detalle de la auditoría/);
    await expect(filas.first()).toBeVisible();
    expect(await filas.count()).toBeGreaterThanOrEqual(3);
    await expect(filas.first().getByText(/\d+ ms/)).toBeVisible();

    // Recarga el detalle de la fila más reciente (la auditoría del escenario 3).
    await filas.first().click();
    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("RECHAZADO", { exact: true })).toBeVisible();
    await expect(semaforo.getByText("FALTA_ORDEN_COMPRA")).toBeVisible();

    // JSON inspector plegable → desplegado → copiable (Pydantic + crudo IA).
    await page.getByRole("button", { name: "Ver JSON Estructurado (Pydantic)" }).click();
    await expect(page.getByText("Objeto Pydantic (datos_extraidos)")).toBeVisible();
    await expect(page.getByText("JSON crudo IA (json_crudo_ia)")).toBeVisible();
    await expect(page.getByText('"monto_total"').first()).toBeVisible();
    await page
      .getByRole("button", { name: "Copiar Objeto Pydantic (datos_extraidos) al portapapeles" })
      .click();
    await expect(page.getByText("¡Copiado!")).toBeVisible();

    // Composición final para la captura del README (historial + JSON abiertos).
    await page.getByRole("button", { name: /Historial de auditorías/ }).click();
    await expect(filas.first()).toBeVisible();
    await captura(page, "demo-03-json-historial.png");
  });
});
