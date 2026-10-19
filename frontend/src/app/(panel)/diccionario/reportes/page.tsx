import { Suspense } from "react";
import { ExploradorBasesDic } from "@/features/diccionario/explorador-bases";

export default function PaginaReportesDic() {
  return (
    <Suspense>
      <ExploradorBasesDic />
    </Suspense>
  );
}
