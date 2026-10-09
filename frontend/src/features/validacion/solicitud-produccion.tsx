"use client";

import { Check, ClipboardCopy, Save } from "lucide-react";
import { useState } from "react";
import { Aviso, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";

/** Mensaje único para Producción: copiar o guardar en data/outputs/solicitudes. `guardar` vuelve a verificar en la API. */
export function SolicitudProduccion({ texto, guardar }: { texto: string; guardar: () => Promise<{ archivo: string }> }) {
  const [copiado, setCopiado] = useState(false);
  const [guardado, setGuardado] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function copiar() {
    await navigator.clipboard.writeText(texto);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  }
  async function guardarArchivo() {
    setError(null);
    try {
      setGuardado((await guardar()).archivo);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border bg-card p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold">Solicitud para Producción</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={copiar}>{copiado ? <Check /> : <ClipboardCopy />} {copiado ? "Copiado" : "Copiar"}</Button>
          <Button variant="outline" size="sm" onClick={guardarArchivo}><Save /> Guardar</Button>
        </div>
      </div>
      <pre className="font-mono text-xs whitespace-pre-wrap">{texto}</pre>
      {guardado && <Aviso tono="exito">Guardada en data/outputs/solicitudes/{guardado}. Cuando Producción confirme, vuelve a verificar.</Aviso>}
      {error && <ErrorEnLinea titulo="No se pudo guardar la solicitud" detalle={error} />}
    </div>
  );
}
