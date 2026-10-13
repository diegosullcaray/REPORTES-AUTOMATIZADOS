import assert from "node:assert/strict";
import { test } from "node:test";
import type { Ejecucion } from "../../lib/tipos";
import { agruparProcesos } from "./proceso.ts";

let n = 0;
const ej = (reporte: string, estado: Ejecucion["estado"], inicio: string, args: string[], archivos: string[] = []): Ejecucion =>
  ({ id: String(++n), reporte, argumentos: [reporte, ...args], estado, codigo: null, inicio, fin: null, archivos });
const C = ["--fecha-corte", "2026-10-12"];
const estados = (p: ReturnType<typeof agruparProcesos>[number]) => p.pasos.map((x) => `${x.id}:${x.estado}:${x.intentos}`);

test("agrupa por reporte y corte, del más reciente al más antiguo", () => {
  const ps = agruparProcesos([
    ej("garra", "ok", "2026-10-01T10:00", ["--fecha-corte", "2026-09-30"]),
    ej("cartera", "ok", "2026-10-13T08:00", [...C, "--correo", "prueba"]),
    ej("cartera", "ok", "2026-10-12T08:00", ["--fecha-corte", "2026-10-11", "--correo", "prueba"]),
    ej("cartera", "error", "2026-10-13T07:00", [...C, "--correo", "prueba"]),
  ]);
  assert.deepEqual(ps.map((p) => [p.reporte, p.corte, p.ejecuciones.length]), [["cartera", "2026-10-12", 2], ["cartera", "2026-10-11", 1], ["garra", "2026-09-30", 1]]);
});

test("cartera completa: Excel, prueba y envío a la lista", () => {
  const [p] = agruparProcesos([
    ej("cartera", "ok", "2026-10-13T08:00", [...C, "--correo", "prueba"], ["c.xlsx", "r.jpg"]),
    ej("cartera", "ok", "2026-10-13T09:00", [...C, "--conforme", "--correo", "todos"]),
  ]);
  assert.deepEqual(estados(p), ["excel:hecho:1", "prueba:hecho:1", "envio:hecho:1"]);
  assert.equal(p.estado, "completo");
});

test("falta el envío: queda incompleto con el paso marcado como falta", () => {
  const [p] = agruparProcesos([ej("cartera", "ok", "2026-10-13T08:00", [...C, "--correo", "prueba"], ["c.xlsx"])]);
  assert.deepEqual(estados(p), ["excel:hecho:1", "prueba:hecho:1", "envio:falta:0"]);
  assert.equal(p.estado, "incompleto");
});

test("Excel generado pero el correo de prueba falló", () => {
  const [p] = agruparProcesos([ej("cartera", "error", "2026-10-13T08:00", [...C, "--correo", "prueba"], ["c.xlsx"])]);
  assert.deepEqual(estados(p), ["excel:hecho:1", "prueba:fallo:1", "envio:falta:0"]);
  assert.equal(p.estado, "fallo");
});

test("falló antes del Excel: la prueba no se intentó; un reintento correcto lo deja al día", () => {
  const corridas = [ej("cartera", "tablas_desactualizadas", "2026-10-13T07:00", [...C, "--correo", "prueba"])];
  assert.deepEqual(estados(agruparProcesos(corridas)[0]), ["excel:fallo:1", "prueba:falta:0", "envio:falta:0"]);
  corridas.push(ej("cartera", "ok", "2026-10-13T08:00", [...C, "--correo", "prueba"], ["c.xlsx"]));
  assert.deepEqual(estados(agruparProcesos(corridas)[0]), ["excel:hecho:2", "prueba:hecho:1", "envio:falta:0"]);
});

test("reporte sin correo: un solo paso; en curso manda", () => {
  const [p] = agruparProcesos([ej("garra", "error", "2026-10-01T10:00", C), ej("garra", "ejecutando", "2026-10-01T11:00", C)]);
  assert.deepEqual(estados(p), ["generacion:en_curso:2"]);
  assert.equal(p.estado, "en_curso");
});
