import { AppSidebar } from "@/components/app-sidebar";
import { Encabezado } from "@/components/encabezado";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

/** Cascarón de la aplicación (sidebar + migas). El acceso lo exige `proxy.ts`; la pantalla de acceso vive en `(auth)`. */
export default function PanelLayout({ children }: LayoutProps<"/">) {
  return (
    <SidebarProvider style={{ "--sidebar-width": "19.5rem" } as React.CSSProperties}>
      <AppSidebar />
      <SidebarInset className="min-w-0">
        <Encabezado />
        <main className="flex min-h-0 flex-1">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
