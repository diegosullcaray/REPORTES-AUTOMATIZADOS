import type { Metadata } from "next";
import { BotonTema, Rail, SCRIPT_TEMA } from "@/components/shell";
import "./globals.css";

export const metadata: Metadata = {
  title: "Reportes automatizados · MIS",
  description: "Validación, ejecución y entrega de los reportes de Financiera Confianza",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="es" suppressHydrationWarning className="h-full antialiased">
      <head>
        <script dangerouslySetInnerHTML={{ __html: SCRIPT_TEMA }} />
      </head>
      <body className="min-h-full">
        <Rail />
        <div className="flex min-h-screen flex-col pb-16 md:pb-0 md:pl-[var(--mis-sidebar-col1-w)]">
          <header className="mis-header sticky top-0 z-30 flex h-[var(--mis-header-h)] items-center justify-between px-4">
            <span className="text-[15px] font-semibold text-[var(--mis-primary-text)]">Reportes automatizados</span>
            <BotonTema />
          </header>
          <main className="flex w-full flex-1 flex-col p-2 sm:p-4">{children}</main>
        </div>
      </body>
    </html>
  );
}
