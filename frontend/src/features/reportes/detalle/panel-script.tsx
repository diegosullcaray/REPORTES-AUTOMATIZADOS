"use client";

import { Check, Copy, Pencil, Save, X } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";

/** Código resaltado con Shiki (carga perezosa: no entra en el bundle inicial). Sale ya escapado: solo viaja texto del repo. */
function Codigo({ codigo }: { codigo: string }) {
  const [html, setHtml] = useState<string | null>(null);
  useEffect(() => {
    let vigente = true;
    import("shiki").then(({ codeToHtml }) => codeToHtml(codigo, { lang: "python", theme: "github-dark" })).then((h) => vigente && setHtml(h));
    return () => { vigente = false; };
  }, [codigo]);
  // Mientras carga, el texto plano evita el salto de layout.
  return html
    ? <div className="script-codigo" dangerouslySetInnerHTML={{ __html: html }} />
    : <pre className="p-3 font-mono text-[12px]" style={{ color: "var(--terminal-fg)" }}>{codigo}</pre>;
}

/** Código del módulo del reporte en una consola: se puede editar y guardar (rige desde la siguiente ejecución). */
export function PanelScript({ reporte }: { reporte: string }) {
  const { datos, error, cargando, recargar } = useConsulta(`script/${reporte}`, () => api.script(reporte));
  const [copiado, setCopiado] = useState(false);
  const [borrador, setBorrador] = useState<string | null>(null); // null = solo lectura
  const [guardando, setGuardando] = useState(false);
  if (error) return <ErrorEnLinea titulo="No se pudo leer el script" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={8} />;
  if (!datos) return null;
  const copiar = () => navigator.clipboard.writeText(datos.codigo).then(() => { setCopiado(true); setTimeout(() => setCopiado(false), 1500); });
  const guardar = () => {
    if (borrador === null || guardando) return;
    setGuardando(true);
    api.guardarScript(reporte, borrador)
      .then(() => { toast.success("Script guardado. Rige desde la siguiente ejecución."); setBorrador(null); recargar(); })
      .catch((e: Error) => toast.error(e.message))
      .finally(() => setGuardando(false));
  };
  const sinCambios = borrador === datos.codigo;
  return (
    <div className="overflow-hidden rounded-lg border" style={{ background: "var(--terminal-bg)" }}>
      <div className="flex items-center justify-between gap-2 border-b border-white/10 px-3 py-1.5">
        <span className="min-w-0 truncate font-mono text-xs" style={{ color: "var(--terminal-tenue)" }}>{datos.ruta}{borrador !== null && !sinCambios ? " · sin guardar" : ""}</span>
        <div className="flex shrink-0 gap-1 text-[var(--terminal-tenue)]">
          {borrador === null ? (
            <>
              <Button variant="ghost" size="sm" onClick={copiar}>{copiado ? <Check /> : <Copy />} {copiado ? "Copiado" : "Copiar"}</Button>
              <Button variant="ghost" size="sm" onClick={() => setBorrador(datos.codigo)}><Pencil /> Editar</Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" onClick={() => setBorrador(null)} disabled={guardando}><X /> Descartar</Button>
              <Button variant="ghost" size="sm" onClick={guardar} disabled={guardando || sinCambios}><Save /> {guardando ? "Guardando…" : "Guardar"}</Button>
            </>
          )}
        </div>
      </div>
      <div className="max-h-[70vh] overflow-auto">
        {borrador === null ? <Codigo codigo={datos.codigo} /> : (
          <textarea
            autoFocus spellCheck={false} aria-label={`Editar ${datos.ruta}`} value={borrador} onChange={(e) => setBorrador(e.target.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); guardar(); }
              if (e.key === "Tab") { // sangría de 4 espacios en vez de saltar el foco
                e.preventDefault();
                const { selectionStart: i, selectionEnd: f } = e.currentTarget;
                setBorrador(borrador.slice(0, i) + "    " + borrador.slice(f));
                requestAnimationFrame(() => e.currentTarget.setSelectionRange(i + 4, i + 4));
              }
            }}
            className="block min-h-[60vh] w-full resize-none bg-transparent p-3 font-mono text-[12px] leading-[1.6] whitespace-pre outline-none"
            style={{ color: "var(--terminal-fg)" }} wrap="off" rows={Math.min(borrador.split("\n").length + 1, 40)}
          />
        )}
      </div>
    </div>
  );
}
