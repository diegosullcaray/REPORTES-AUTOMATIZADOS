import { SidebarReportes } from "@/features/reportes/sidebar-reportes";

export default function LayoutReportes({ children }: LayoutProps<"/reportes">) {
  return (
    <div className="flex min-w-0 flex-1">
      <SidebarReportes />
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
