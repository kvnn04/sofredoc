/**
 * E2E del flujo de auditoría (DESIGN-05 §3, CU-02, RN-5-04).
 *
 * Los 4 escenarios obligatorios usan los 3 ejemplos pre-cargados (resultados
 * esperados conocidos: APROBADO / RECHAZADO-R3 / RECHAZADO-R4) y cierran con
 * el JSON inspector + historial. Van en `serial` porque el historial acumula
 * las auditorías previas sobre la BD efímera del backend (ver playwright.config.ts).
 *
 * El escenario 5 cubre la subida de PDFs propios: validaciones client-side de
 * RN-4-03 (`.txt` → PDF_INVALIDO, > 5 MB → ARCHIVO_MUY_GRANDE) sin perder el
 * empty-state (CU-05), y el flujo completo con un PDF real (blob en el visor,
 * RN-4-04). Para asertar el estado "Auditando…" se amplifica la latencia del
 * POST con `page.route` (el backend real no se toca).
 *
 * Los escenarios 6–10 (extensión, ADR-05-08) cubren: admisión R0 de un REMITO
 * con la fixture nueva del MockExtractor (1 sola regla evaluada, sin
 * cortocircuito), `PDF_SIN_TEXTO` y el tope de 10 páginas validados en el
 * backend real (PDFs fixture commiteados en `qa/e2e/fixtures/`, generados por
 * `backend/scripts/generar_fixtures_e2e.py`), la red caída (`ERROR_RED`) y el
 * `EXTRACCION_FALLIDA` (502 simulado con `page.route` sin tocar el backend):
 * en ambos el resultado previo se conserva (CU-05).
 *
 * Con `CAPTURAS=1` cada escenario guarda una captura en `docs/capturas/`
 * (para el README); en CI y corridas normales no escribe nada.
 */
import { mkdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test, type Page } from "@playwright/test";

const SEMAFORO = "Semáforo de auditoría";
const CODIGOS_ERROR =
  /ERROR_CUIT_INVALIDO|PROVEEDOR_NO_REGISTRADO|DISCREPANCIA_CONTABLE|FALTA_ORDEN_COMPRA|COMPROBANTE_VENCIDO|REMITO_NO_AUDITABLE/;
/** Códigos de las reglas R1–R5 (R0 no pertenece al semáforo de reglas de fondo). */
const CODIGOS_R1_A_R5 =
  /ERROR_CUIT_INVALIDO|PROVEEDOR_NO_REGISTRADO|DISCREPANCIA_CONTABLE|FALTA_ORDEN_COMPRA|COMPROBANTE_VENCIDO/;

function ejemplo(nombre: string) {
  return `Auditar ejemplo: ${nombre}`;
}

function fixtureE2E(nombre: string): Buffer {
  return readFileSync(resolve("qa/e2e/fixtures", nombre));
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
    // El visor recibió el PDF del ejemplo (iframe con la URL de la API).
    await expect(page.locator('iframe[src*="/api/v1/ejemplos/"]')).toBeVisible();

    await captura(page, "demo-01-aprobado.png");
  });

  test("2) ejemplo con desvío → RECHAZADO por R3 (DISCREPANCIA_CONTABLE)", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: ejemplo("Factura con desvío de monto") }).click();

    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("RECHAZADO", { exact: true })).toBeVisible();
    await expect(semaforo.getByText("DISCREPANCIA_CONTABLE")).toBeVisible();
    // Los montos comparados aparecen en el mensaje de R3 (checklist MOD-04 ítem 4).
    await expect(semaforo.getByText("$28.200,00")).toBeVisible();
    await expect(semaforo.getByText("$30.000,00")).toBeVisible();
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

  test("5) subida propia: PDF_INVALIDO / ARCHIVO_MUY_GRANDE sin perder estado + flujo completo", async ({ page }) => {
    await page.goto("/");

    // CU-01 Given: el panel arranca en empty-state.
    const estadoInicial = page.getByText("Pantalla lista para auditar");
    await expect(estadoInicial).toBeVisible();

    const banner = page.getByRole("alert");
    const subir = page.getByRole("button", { name: "Subir un PDF propio (máximo 5 MB)" });

    // a) Un .txt no es un PDF → PDF_INVALIDO (client-side, RN-4-03), sin llamada
    //    a la API y sin destruir el estado previo (CU-05).
    await page.setInputFiles('input[type="file"]', {
      name: "notas.txt",
      mimeType: "text/plain",
      buffer: Buffer.from("esto no es un pdf"),
    });
    await expect(banner.getByText("PDF_INVALIDO")).toBeVisible();
    await expect(estadoInicial).toBeVisible();

    // b) PDF de 6 MB supera el tope de 5 MB → ARCHIVO_MUY_GRANDE (RN-4-03).
    await page.setInputFiles('input[type="file"]', {
      name: "factura-grande.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.alloc(6 * 1024 * 1024),
    });
    await expect(banner.getByText("ARCHIVO_MUY_GRANDE")).toBeVisible();
    await expect(estadoInicial).toBeVisible();

    // c) Flujo completo con un PDF real: se amplifica la latencia del POST
    //    (800 ms) para asertar el estado de carga — el backend queda intacto.
    await page.route("**/api/v1/auditar", async (ruta) => {
      await new Promise((res) => setTimeout(res, 800));
      await ruta.continue();
    });
    const pdfReal = readFileSync(resolve("backend/data/ejemplos/factura-aprobada-001.pdf"));
    await page.setInputFiles('input[type="file"]', {
      name: "mi-factura.pdf",
      mimeType: "application/pdf",
      buffer: pdfReal,
    });
    await expect(subir).toBeDisabled();
    await expect(subir).toContainText("Auditando…");
    await expect(page.getByText("Auditando documento…")).toBeVisible(); // skeleton

    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("APROBADO", { exact: true })).toBeVisible();
    await expect(subir).toBeEnabled();
    await expect(subir).toContainText("Subir PDF");
    // El visor muestra el archivo subido como blob URL (RN-4-04).
    await expect(page.locator('iframe[src^="blob:"]')).toBeVisible();

    await captura(page, "demo-04-subida-propia.png");
  });
});

test.describe.serial("Escenarios extendidos (ADR-05-08)", () => {
  test("6) remito subido → admisión R0: 1 sola regla, sin evaluar R1–R5", async ({ page }) => {
    await page.goto("/");
    await page.setInputFiles('input[type="file"]', {
      name: "remito-transporte-2026.pdf",
      mimeType: "application/pdf",
      buffer: fixtureE2E("remito-transporte-2026.pdf"),
    });

    const semaforo = page.getByRole("region", { name: SEMAFORO });
    await expect(semaforo.getByText("RECHAZADO", { exact: true })).toBeVisible();
    await expect(semaforo.getByText("REMITO_NO_AUDITABLE")).toBeVisible();
    // R0 corta el flujo (RN-08): el semáforo tiene 1 sola fila (la admisión).
    await expect(semaforo.getByRole("listitem")).toHaveCount(1);
    await expect(semaforo.getByText("R0")).toBeVisible();
    await expect(semaforo.getByText("Admisión de comprobante")).toBeVisible();
    // Ninguna regla de fondo R1–R5 fue evaluada (sin cortocircuito).
    await expect(semaforo.getByText(CODIGOS_R1_A_R5)).toHaveCount(0);

    await captura(page, "demo-05-remito-r0.png");
  });

  test("7) PDF sin capa de texto → PDF_SIN_TEXTO (422 del backend) sin perder estado", async ({ page }) => {
    await page.goto("/");
    const estadoInicial = page.getByText("Pantalla lista para auditar");
    await expect(estadoInicial).toBeVisible();

    await page.setInputFiles('input[type="file"]', {
      name: "pdf-escaneado-grafico.pdf",
      mimeType: "application/pdf",
      buffer: fixtureE2E("pdf-escaneado-grafico.pdf"),
    });

    const banner = page.getByRole("alert");
    await expect(banner.getByText("PDF_SIN_TEXTO")).toBeVisible();
    await expect(estadoInicial).toBeVisible(); // CU-05: el error no destruye el estado
  });

  test("8) PDF de 11 páginas → PDF_INVALIDO validado en el backend (tope 10)", async ({ page }) => {
    await page.goto("/");
    const estadoInicial = page.getByText("Pantalla lista para auditar");
    await expect(estadoInicial).toBeVisible();

    // Client-side pasa (es un PDF chico): la validación de páginas es del servidor.
    await page.setInputFiles('input[type="file"]', {
      name: "factura-11-paginas.pdf",
      mimeType: "application/pdf",
      buffer: fixtureE2E("factura-11-paginas.pdf"),
    });

    const banner = page.getByRole("alert");
    await expect(banner.getByText("PDF_INVALIDO")).toBeVisible();
    await expect(estadoInicial).toBeVisible();
  });

  test("9) red caída → ERROR_RED y el resultado previo se conserva (CU-05)", async ({ page }) => {
    await page.goto("/");
    const semaforo = page.getByRole("region", { name: SEMAFORO });

    // Arrange: un resultado previo en pantalla (ejemplo aprobado).
    await page.getByRole("button", { name: ejemplo("Factura Proveedor Homologado #001") }).click();
    await expect(semaforo.getByText("APROBADO", { exact: true })).toBeVisible();

    // Act: la próxima llamada de auditoría se corta a nivel de red.
    await page.route("**/api/v1/auditar", (ruta) => ruta.abort());
    await page.getByRole("button", { name: ejemplo("Factura con desvío de monto") }).click();

    // El banner tipado explica la caída…
    const banner = page.getByRole("alert");
    await expect(banner.getByText("ERROR_RED")).toBeVisible();
    await expect(banner.getByText("No se pudo conectar con el backend")).toBeVisible();
    // …y CU-05: el resultado previo sigue en pantalla.
    await expect(semaforo.getByText("APROBADO", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Subir un PDF propio (máximo 5 MB)" })).toBeEnabled();
  });

  test("10) EXTRACCION_FALLIDA (502 simulado) → banner tipado y resultado previo intacto", async ({ page }) => {
    await page.goto("/");
    const semaforo = page.getByRole("region", { name: SEMAFORO });

    // Arrange: un resultado previo en pantalla (ejemplo aprobado).
    await page.getByRole("button", { name: ejemplo("Factura Proveedor Homologado #001") }).click();
    await expect(semaforo.getByText("APROBADO", { exact: true })).toBeVisible();

    // Act: el POST responde 502 con el cuerpo de error del contrato (§3).
    // El fulfill intercepta la llamada: el backend nunca la recibe (0 créditos).
    await page.route("**/api/v1/auditar", (ruta) =>
      ruta.fulfill({
        status: 502,
        contentType: "application/json",
        body: JSON.stringify({
          error: {
            codigo: "EXTRACCION_FALLIDA",
            mensaje: "La respuesta del LLM no validó contra el esquema tras 2 intentos (simulado).",
          },
        }),
      }),
    );
    await page.getByRole("button", { name: ejemplo("Factura con desvío de monto") }).click();

    // El banner muestra el código de error tipado del contrato…
    const banner = page.getByRole("alert");
    await expect(banner.getByText("EXTRACCION_FALLIDA")).toBeVisible();
    await expect(banner.getByText("no validó contra el esquema")).toBeVisible();
    // …y CU-05: el resultado previo sigue en pantalla.
    await expect(semaforo.getByText("APROBADO", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Subir un PDF propio (máximo 5 MB)" })).toBeEnabled();
  });
});
