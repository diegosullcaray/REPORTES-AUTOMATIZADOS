import assert from "node:assert/strict";
import { test } from "node:test";
import type { Ejecucion, ReporteResumen } from "../../lib/tipos";
import { pendientesDelCierre, resumenSemanal } from "./metricas.ts";

const ej = (reporte: string, estado: Ejecucion["estado"], inicio: string, args: string[] = []): Ejecucion =>
  ({ id: inicio, reporte, argumentos: [reporte, ...args], estado, codigo: null, inicio, fin: null, archivos: [] });

test("resumen semanal: total, éxito y variación frente a la semana previa", () => {
  const ahora = Date.parse("2026-10-07T12:00:00");
  const r = resumenSemanal([
    ej("a", "ok", "2026-10-06T10:00:00"), ej("b", "error", "2026-10-05T10:00:00"),
    ej("c", "ok", "2026-09-28T10:00:00"), // semana previa
  ], ahora);
  assert.deepEqual([r.total, r.correctas, r.exito, r.variacion], [2, 1, 50, "+100% vs 7 días previos"]);
});

test("cierre: un mensual cuenta como listo con una ejecución correcta del mismo corte (o del mes con --mes)", () => {
  const rep = (nombre: string, frecuencia: ReporteResumen["frecuencia"]) => ({ nombre, frecuencia }) as ReporteResumen;
  const reportes = [rep("garra", "mensual"), rep("indicadores", "mensual"), rep("fondeo", "mensual"), rep("cartera", "diaria")];
  const c = pendientesDelCierre(reportes, [
    ej("garra", "ok", "2026-10-01T09:00:00", ["--fecha-corte", "2026-09-30"]),
    ej("indicadores", "ok", "2026-10-01T09:00:00", ["--mes", "2026-09"]),
    ej("fondeo", "error", "2026-10-01T09:00:00", ["--fecha-corte", "2026-09-30"]),
  ], "2026-09-30");
  assert.deepEqual([c.total, c.listos, c.pendientes.map((r) => r.nombre)], [3, 2, ["fondeo"]]);
});
