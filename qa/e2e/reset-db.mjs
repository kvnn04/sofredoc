/**
 * Borra la BD SQLite efímera del E2E antes de que arranque el backend de
 * Playwright (el `webServer` se inicia antes del globalSetup, por eso el
 * reset vive en el comando de arranque). RN-5-05: nunca toca
 * `backend/data/sofredoc.db`.
 */
import { rmSync } from "node:fs";
import { resolve } from "node:path";

const artefactos = resolve(import.meta.dirname, "..", "artifacts");
for (const sufijo of ["", "-wal", "-shm"]) {
  rmSync(resolve(artefactos, `e2e-sofredoc.db${sufijo}`), { force: true });
}
