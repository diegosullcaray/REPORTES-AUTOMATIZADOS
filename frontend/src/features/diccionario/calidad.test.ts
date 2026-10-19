import assert from "node:assert/strict";
import { test } from "node:test";
import type { DicBase, DicHallazgo } from "../../lib/tipos";
import { avancePorBase, porRegla } from "./calidad.ts";

const h = (regla: string, nivel: string): DicHallazgo => ({ nivel, regla, origen: "analisis", objeto: "x", detalle: "" });

test("cuenta errores y avisos por regla, ordena por total y deja fuera lo informativo", () => {
  const r = porRegla([h("b", "aviso"), h("a", "error"), h("a", "aviso"), h("a", "error"), h("c", "info"), h("b", "aviso")]);
  assert.deepEqual(r, [["a", { error: 2, aviso: 1 }], ["b", { error: 0, aviso: 2 }]]);
});

test("a igual total, por nombre de regla (el orden no cambia entre cargas)", () => {
  assert.deepEqual(porRegla([h("z", "aviso"), h("m", "aviso")]).map(([n]) => n), ["m", "z"]);
});

test("el avance se mide en % de cada base, así la chica se ve igual que la grande", () => {
  const base = (nombre: string, procedimientos: number, extraidos: number, validados: number): DicBase => ({ base: nombre, procedimientos, extraidos, validados, tablas: 0 });
  const [grande, chica, vacia] = [base("grande", 200, 150, 100), base("chica", 2, 2, 1), base("vacia", 0, 0, 0)];
  const r = avancePorBase([chica, vacia, grande]);
  assert.deepEqual(r.map((x) => x.base), ["grande", "chica"]);                          // sin procedimientos no hay barra
  assert.deepEqual([r[0].validados, r[0].extraidos, r[0].pendientes], [100, 50, 50]);
  assert.deepEqual([r[1].pctValidados, r[1].pctExtraidos, r[1].pctPendientes], [50, 50, 0]);
});
