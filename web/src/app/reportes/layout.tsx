import { SidebarReportes } from "@/features/reportes/sidebar-reportes";

export default function LayoutReportes({ children }: LayoutProps<"/reportes">) {
  return (
    <>
      <SidebarReportes />
      <div className="md:pl-72">{children}</div>
    </>
  );
}
