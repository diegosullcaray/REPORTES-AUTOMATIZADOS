"use client";

import {
  type Column, type ColumnDef, flexRender, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel,
  type SortingState, useReactTable, type VisibilityState,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ArrowUpDown, ChevronLeft, ChevronRight, Columns3, RefreshCw, Search } from "lucide-react";
import { useState, type ReactNode } from "react";
import { EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuGroup, DropdownMenuLabel, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { LucideIcon } from "lucide-react";

/** Encabezado que ordena al pulsarlo (asc → desc → sin orden), con el sentido visible. */
export function Ordenable<T>({ column, children }: { column: Column<T>; children: ReactNode }) {
  const orden = column.getIsSorted();
  const Icono = orden === "asc" ? ArrowUp : orden === "desc" ? ArrowDown : ArrowUpDown;
  return (
    <Button variant="ghost" size="sm" className="-ml-2 h-8" onClick={() => column.toggleSorting(orden === "asc")}>
      {children}
      <Icono className={orden ? "" : "text-muted-foreground"} />
    </Button>
  );
}

interface Props<T> {
  columnas: ColumnDef<T, unknown>[];
  datos: T[] | undefined;
  cargando: boolean;
  error: string | null;
  onRecargar: () => void;
  /** Texto de ayuda del buscador global (busca en todas las columnas con texto). */
  buscar?: string;
  /** Filtros propios de la vista (selects), a la derecha del buscador. */
  filtros?: ReactNode;
  vacio: { titulo: string; descripcion?: string; icono?: LucideIcon };
  ordenInicial?: SortingState;
  ocultas?: VisibilityState;
  porPagina?: number;
  /** Nombres legibles de las columnas para el menú «Columnas». */
  nombres?: Record<string, string>;
}

/**
 * Tabla de datos (patrón Dokploy con TanStack): buscador, filtros, recarga, columnas visibles, orden y paginación.
 * Estados en orden: error → esqueleto de la propia tabla → vacío → filas.
 */
export function TablaDatos<T>({ columnas, datos, cargando, error, onRecargar, buscar, filtros, vacio, ordenInicial = [], ocultas = {}, porPagina = 15, nombres = {} }: Props<T>) {
  const [sorting, setSorting] = useState<SortingState>(ordenInicial);
  const [visibilidad, setVisibilidad] = useState<VisibilityState>(ocultas);
  const [globalFilter, setGlobalFilter] = useState("");
  const [paginacion, setPaginacion] = useState({ pageIndex: 0, pageSize: porPagina });

  // eslint-disable-next-line react-hooks/incompatible-library -- TanStack Table devuelve funciones no memoizables; es lo esperado
  const tabla = useReactTable({
    data: datos ?? [],
    columns: columnas,
    state: { sorting, columnVisibility: visibilidad, globalFilter, pagination: paginacion },
    onSortingChange: setSorting,
    onColumnVisibilityChange: setVisibilidad,
    onGlobalFilterChange: setGlobalFilter,
    onPaginationChange: setPaginacion,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    autoResetPageIndex: false,
  });

  const filas = tabla.getRowModel().rows;
  const total = tabla.getFilteredRowModel().rows.length;
  const desde = total === 0 ? 0 : paginacion.pageIndex * paginacion.pageSize + 1;
  const hasta = Math.min(total, (paginacion.pageIndex + 1) * paginacion.pageSize);
  const visibles = tabla.getVisibleLeafColumns().length;
  const refrescando = cargando && !!datos;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        {buscar && (
          <label className="relative w-full sm:max-w-xs">
            <span className="sr-only">{buscar}</span>
            <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input value={globalFilter} placeholder={buscar} className="pl-8"
              onChange={(e) => { setGlobalFilter(e.target.value); setPaginacion((p) => ({ ...p, pageIndex: 0 })); }} />
          </label>
        )}
        {filtros}
        <div className="ml-auto flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={onRecargar} disabled={cargando} aria-label="Actualizar">
            <RefreshCw className={refrescando ? "animate-spin" : ""} />
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger render={<Button variant="outline" />}><Columns3 /> Columnas</DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuGroup>
                <DropdownMenuLabel>Columnas visibles</DropdownMenuLabel>
                {tabla.getAllLeafColumns().filter((c) => c.getCanHide()).map((c) => (
                  <DropdownMenuCheckboxItem key={c.id} checked={c.getIsVisible()} onCheckedChange={(v) => c.toggleVisibility(!!v)}>
                    {nombres[c.id] ?? c.id}
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {error ? (
        <ErrorEnLinea titulo="No se pudieron cargar los datos" detalle={error} onReintentar={onRecargar} />
      ) : (
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader className="bg-muted/50">
              {tabla.getHeaderGroups().map((g) => (
                <TableRow key={g.id} className="hover:bg-transparent">
                  {g.headers.map((h) => (
                    <TableHead key={h.id} className="h-10 whitespace-nowrap">
                      {h.isPlaceholder ? null : flexRender(h.column.columnDef.header, h.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {cargando && !datos ? (
                Array.from({ length: 6 }, (_, i) => (
                  <TableRow key={i} className="hover:bg-transparent">
                    {Array.from({ length: visibles }, (_, j) => <TableCell key={j}><Skeleton className="h-5 w-full" /></TableCell>)}
                  </TableRow>
                ))
              ) : filas.length === 0 ? (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={visibles}>
                    {datos?.length ? <EstadoVacio titulo="Sin resultados" descripcion="Ninguna fila coincide con la búsqueda o los filtros." /> : <EstadoVacio {...vacio} />}
                  </TableCell>
                </TableRow>
              ) : (
                filas.map((f) => (
                  <TableRow key={f.id}>
                    {f.getVisibleCells().map((c) => <TableCell key={c.id} className="py-2.5">{flexRender(c.column.columnDef.cell, c.getContext())}</TableCell>)}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}

      {!error && total > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
          <span>{desde}–{hasta} de {total}</span>
          <div className="flex items-center gap-2">
            <span>Página {paginacion.pageIndex + 1} de {tabla.getPageCount()}</span>
            <Button variant="outline" size="icon-sm" onClick={() => tabla.previousPage()} disabled={!tabla.getCanPreviousPage()} aria-label="Página anterior"><ChevronLeft /></Button>
            <Button variant="outline" size="icon-sm" onClick={() => tabla.nextPage()} disabled={!tabla.getCanNextPage()} aria-label="Página siguiente"><ChevronRight /></Button>
          </div>
        </div>
      )}
    </div>
  );
}
