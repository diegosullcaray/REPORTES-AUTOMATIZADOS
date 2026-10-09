import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

/** Guardas de color: contraste AA de los tokens de MIS en claro y oscuro, y nada de color fuera de los tokens en los componentes. */

const SRC = fileURLToPath(new URL("..", import.meta.url));
const css = readFileSync(join(SRC, "app", "tokens.css"), "utf-8");
const corte = css.indexOf(".dark {");

const variables = (texto: string) => Object.fromEntries([...texto.matchAll(/--(mis-[\w-]+):\s*([^;]+);/g)].map((m) => [m[1], m[2].trim()]));
const claro = variables(css.slice(0, corte));
const oscuro = { ...claro, ...variables(css.slice(corte)) };

function rgb(valor: string | undefined): [number, number, number] {
  const hex = valor?.match(/^#([0-9a-f]{6})$/i)?.[1];
  assert.ok(hex, `el token no es un #rrggbb: ${valor}`);
  return [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16)) as [number, number, number];
}
const luminancia = (c: number[]) => {
  const [r, g, b] = c.map((x) => (x / 255 <= 0.03928 ? x / 255 / 12.92 : ((x / 255 + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};
const contraste = (a: number[], b: number[]) => {
  const [alto, bajo] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return (alto + 0.05) / (bajo + 0.05);
};

// Texto sobre su fondo: mínimo AA (4.5) en los dos temas. `mis-text-tertiary` queda fuera a propósito (3.0 en claro): solo decorativo.
const PARES: [string, string][] = [
  ["text-primary", "bg"], ["text-secondary", "bg"], ["text-primary", "surface"], ["text-secondary", "surface"], ["text-secondary", "panel-bg"],
  ["primary-text", "bg"], ["primary-text", "surface"], ["text-on-primary", "primary"],
  ["success", "success-light"], ["warning", "warning-light"], ["danger", "danger-light"],
  ["primary-text", "secondary-light"], ["text-secondary", "primary-light"],
];

for (const [tema, tokens] of [["claro", claro], ["oscuro", oscuro]] as const) {
  test(`contraste AA de los tokens de MIS en tema ${tema}`, () => {
    for (const [texto, fondo] of PARES) {
      const ratio = contraste(rgb(tokens[`mis-${texto}`]), rgb(tokens[`mis-${fondo}`]));
      assert.ok(ratio >= 4.5, `${texto} sobre ${fondo} en ${tema}: ${ratio.toFixed(2)}:1 (mínimo 4.5)`);
    }
  });
}

function archivos(dir: string): string[] {
  return readdirSync(dir).flatMap((n) => {
    const ruta = join(dir, n);
    return statSync(ruta).isDirectory() ? archivos(ruta) : /\.(tsx|ts)$/.test(n) && !n.endsWith(".test.ts") ? [ruta] : [];
  });
}

test("los componentes no usan colores fuera de los tokens --mis-*", () => {
  const PALETA = /\b(?:bg|text|border|ring|fill|stroke|from|to|via)-(?:red|green|blue|yellow|amber|orange|emerald|sky|slate|gray|zinc|neutral|stone|lime|teal|cyan|indigo|violet|purple|pink|rose|black)(?:-\d+)?\b/;
  const CRUDO = /#[0-9a-f]{3,8}\b|rgba?\(|hsla?\(|oklch\(/i;
  const malos = archivos(SRC).flatMap((f) => {
    const texto = readFileSync(f, "utf-8");
    return [PALETA, CRUDO].filter((r) => r.test(texto)).map((r) => `${f.slice(SRC.length)} → ${texto.match(r)?.[0]}`);
  });
  assert.deepEqual(malos, []);
});

test("la marca como texto usa --mis-primary-text (se aclara en oscuro) y el texto informativo no usa el terciario", () => {
  const malos = archivos(SRC).flatMap((f) => {
    const texto = readFileSync(f, "utf-8");
    return [/(?<![\w-])text-primary(?![\w-])/, /mis-text-tertiary/].filter((r) => r.test(texto)).map((r) => `${f.slice(SRC.length)} → ${r}`);
  });
  assert.deepEqual(malos, []);
});
