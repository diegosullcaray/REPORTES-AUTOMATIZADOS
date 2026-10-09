"use client";

import { Check, ClipboardCopy, Save, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { ESTADO_TABLA, errorDeCorte, fecha } from "@/lib/formato";
import type { ReporteDetalle, Verificacion } from "@/lib/tipos";

interface Props {
  reporte: ReporteDetalle;
  corte: string; // se elige una sola vez, junto a las pestañas
  verificacion: Verificacion | null;
  onVerificacion: (v: Verificacion | null) => void;
}

/** ¿Las tablas llegaron al corte? Si no, mensaje listo para Producción. Solo hace SELECT. */
export function PanelValidacion({ reporte, corte, verificacion, onVerificacion }: Props) {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const invalido = errorDeCorte(reporte.frecuencia, corte);
  const vigente = verificacion?.corte === corte ? verificacion : null;

  async function verificar() {
    setCargando(true);
    setError(null);
    try {
      onVerificacion(await api.verificar(reporte.nombre, corte || null));
    } catch (e) {
      onVerificacion(null);
      setError((e as Error).message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={verificar} disabled={cargando || !!invalido}>
          <ShieldCheck /> {cargando ? "Verificando…" : `Verificar tablas al ${corte ? fecha(corte) : "corte"}`}
        </Button>
        {invalido && <span className="text-sm text-muted-foreground">{invalido}</span>}
      </div>

      {error ? (
        <ErrorEnLinea titulo="No se pudo verificar" detalle={error} onReintentar={verificar} />
      ) : cargando ? (
        <EsqueletoFilas filas={Math.min(reporte.tablas.length || 4, 10)} alto="h-8" />
      ) : vigente ? (
        <Resultados v={vigente} reporte={reporte.nombre} />
      ) : (
        <TablasRegistradas reporte={reporte} />
      )}
    </div>
  );
}

function Resultados({ v, reporte }: { v: Verificacion; reporte: string }) {
  const pendientes = v.resultados.filter((r) => r.estado === "DESACTUALIZADA" || r.estado === "NO EXISTE").length;
  const dudosas = v.resultados.filter((r) => r.estado === "ERROR").length;
  return (
    <div className="flex flex-col gap-4">
      {v.listo ? (
        <Aviso tono="exito">✓ Todas las tablas están al día al {fecha(v.corte)}. Puedes pasar a <b>Ejecutar</b>.</Aviso>
      ) : (
        <Aviso tono={pendientes ? "aviso" : "peligro"}>
          {pendientes > 0 && <>✗ {pendientes} tabla(s) sin actualizar al {fecha(v.corte)}. No ejecutes hasta que Producción las cargue. </>}
          {dudosas > 0 && <>{dudosas} tabla(s) no se pudieron verificar (conexión o columna de fecha por confirmar).</>}
        </Aviso>
      )}
      <div className="rounded-lg border bg-card overflow-x-auto">
        <table className="w-full [&_tbody_tr:hover]:bg-muted/50 text-[13px]">
          <thead className="text-left text-[12px] text-[var(--mis-text-secondary)]">
            <tr><th className="p-2">Estado</th><th className="p-2">Tabla</th><th className="p-2">Servidor</th><th className="p-2">Última fecha</th><th className="p-2">Detalle</th></tr>
          </thead>
          <tbody>
            {v.resultados.map((r) => (
              <tr key={r.nombre} className="border-t border-[var(--mis-border)]">
                <td className="p-2"><Chip tono={ESTADO_TABLA[r.estado]}>{r.estado}</Chip></td>
                <td className="p-2 font-mono text-[12px]">{r.nombre}</td>
                <td className="p-2">{r.servidor}</td>
                <td className="p-2 whitespace-nowrap">{fecha(r.ultima_fecha)}</td>
                <td className="min-w-64 p-2 text-[12px] text-[var(--mis-text-secondary)]">{r.detalle}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {v.solicitud && <SolicitudProduccion reporte={reporte} corte={v.corte} texto={v.solicitud} />}
    </div>
  );
}

function SolicitudProduccion({ reporte, corte, texto }: { reporte: string; corte: string; texto: string }) {
  const [copiado, setCopiado] = useState(false);
  const [guardado, setGuardado] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function copiar() {
    await navigator.clipboard.writeText(texto);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  }
  async function guardar() {
    setError(null);
    try {
      setGuardado((await api.guardarSolicitud(reporte, corte)).archivo);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="rounded-lg border bg-card flex flex-col gap-3 p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-[15px] font-semibold">Solicitud para Producción</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={copiar}>{copiado ? <Check /> : <ClipboardCopy />} {copiado ? "Copiado" : "Copiar"}</Button>
          <Button variant="outline" size="sm" onClick={guardar}><Save /> Guardar</Button>
        </div>
      </div>
      <pre className="font-mono text-[12px] whitespace-pre-wrap">{texto}</pre>
      {guardado && <Aviso tono="exito">Guardada en data/outputs/solicitudes/{guardado}. Cuando Producción confirme, vuelve a verificar.</Aviso>}
      {error && <ErrorEnLinea titulo="No se pudo guardar la solicitud" detalle={error} />}
    </div>
  );
}

function TablasRegistradas({ reporte }: { reporte: ReporteDetalle }) {
  if (reporte.tablas.length === 0) return <Aviso tono="neutro">Este reporte no tiene tablas registradas para verificar.</Aviso>;
  return (
    <div className="flex flex-col gap-2">
      <p className="text-[13px] text-[var(--mis-text-secondary)]">
        Tablas que usa el reporte. Pulsa <b>Verificar tablas</b> para comprobar que lleguen al corte (solo lectura).
      </p>
      <div className="rounded-lg border bg-card overflow-x-auto">
        <table className="w-full [&_tbody_tr:hover]:bg-muted/50 text-[13px]">
          <thead className="text-left text-[12px] text-[var(--mis-text-secondary)]">
            <tr><th className="p-2">Tabla</th><th className="p-2">Servidor</th><th className="p-2">Tipo</th><th className="p-2">Columna de fecha</th><th className="p-2">Condición del reporte</th></tr>
          </thead>
          <tbody>
            {reporte.tablas.map((t) => (
              <tr key={t.nombre} className="border-t border-[var(--mis-border)]">
                <td className="p-2 font-mono text-[12px]">{t.nombre}</td>
                <td className="p-2">{t.servidor}</td>
                <td className="p-2"><Chip tono={t.verificable ? "info" : "neutro"}>{t.tipo}</Chip></td>
                <td className="p-2">{t.columna_fecha ?? "—"}{t.confianza === "por_confirmar" && <> <Chip tono="aviso">por confirmar</Chip></>}</td>
                <td className="min-w-64 p-2 text-[12px] text-[var(--mis-text-secondary)]">{t.condicion ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
