"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { tipoLinea, type TipoLinea } from "@/lib/formato";

const COLOR: Record<TipoLinea, string> = {
  ok: "var(--terminal-ok)",
  error: "var(--terminal-error)",
  aviso: "var(--terminal-aviso)",
  paso: "var(--terminal-paso)",
  normal: "var(--terminal-fg)",
};

/** Log en vivo tipo consola: se desplaza solo al final mientras llega salida. */
export function Terminal({ titulo, estado, texto, vacio = "Esperando salida…" }: { titulo: string; estado?: ReactNode; texto: string; vacio?: string }) {
  const caja = useRef<HTMLPreElement>(null);
  useEffect(() => {
    if (caja.current) caja.current.scrollTop = caja.current.scrollHeight;
  }, [texto]);

  return (
    <div className="overflow-hidden rounded-lg border" style={{ background: "var(--terminal-bg)" }}>
      <div className="flex items-center justify-between gap-2 border-b border-white/10 px-3 py-2">
        <span className="font-mono text-xs" style={{ color: "var(--terminal-tenue)" }}>{titulo}</span>
        {estado}
      </div>
      <pre ref={caja} aria-live="polite" className="max-h-[55vh] min-h-40 overflow-auto p-3 font-mono text-[12px] leading-relaxed whitespace-pre-wrap">
        {texto
          ? texto.split("\n").map((l, i) => <div key={i} style={{ color: COLOR[tipoLinea(l)] }}>{l || " "}</div>)
          : <span style={{ color: "var(--terminal-tenue)" }}>{vacio}</span>}
      </pre>
    </div>
  );
}
