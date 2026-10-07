// node --test src/lib  (Node 22+ ejecuta TypeScript directamente)
import assert from "node:assert/strict";
import { test } from "node:test";
import { agruparPorCarpeta, corteDe, haceTiempo, iniciales } from "./formato.ts";

test("tiempo relativo y corte de los argumentos", () => {
  const ahora = Date.parse("2026-10-07T12:00:00");
  assert.equal(haceTiempo("2026-10-07T11:55:00", ahora), "hace 5 minutos");
  assert.equal(haceTiempo("2026-10-06T12:00:00", ahora), "ayer");
  assert.equal(corteDe(["saca-tu-garra", "--fecha-corte", "2026-09-30", "--forzar"]), "2026-09-30");
  assert.equal(corteDe(["indicadores-clientes", "--mes", "2026-09"]), "2026-09");
  assert.equal(corteDe(["listar"]), null);
  assert.equal(iniciales("diego.sullcaray"), "DS");
  assert.equal(iniciales("24681"), "24");
});

test("los sub-reportes de una carpeta del legado quedan bajo un nodo", () => {
  const r = (nombre: string, carpeta: string) => ({ nombre, carpeta });
  const entradas = agruparPorCarpeta([
    r("saldo-medio-vigente", "mensuales/piero/07_saldo_medio_vigente"),
    r("michael-captaciones", "mensuales/piero/09_reporte_mensual_michael_palacios"),
    r("michael-castigos", "mensuales/piero/09_reporte_mensual_michael_palacios"),
  ]);
  assert.equal(entradas.length, 2);
  assert.equal(entradas[0].tipo, "reporte");
  assert.deepEqual(entradas[1].tipo === "nodo" && [entradas[1].orden, entradas[1].titulo, entradas[1].reportes.map((x) => x.nombre)],
    ["09", "Reporte mensual michael palacios", ["michael-captaciones", "michael-castigos"]]);
});
