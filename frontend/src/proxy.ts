import { NextResponse, type NextRequest } from "next/server";

const COOKIE = "reportes_sesion";
const API = process.env.REPORTES_API_URL ?? "http://127.0.0.1:8000";

/** ¿La API acepta esta cookie? Una cookie que existe pero ya no vale (vencida, firmada con otro secreto tras reiniciar la API) no es sesión. */
async function sesionValida(valor: string): Promise<boolean> {
  try {
    const r = await fetch(`${API}/api/sesion`, { headers: { cookie: `${COOKIE}=${valor}` }, cache: "no-store", signal: AbortSignal.timeout(3000) });
    return r.ok;
  } catch {
    return true; // API apagada: se deja pasar para que cada pantalla explique que no hay conexión, en vez de mandar a un login que tampoco funcionaría
  }
}

/** Sin sesión válida solo se ve /login (y se borra la cookie inútil); con ella, /login lleva al inicio. */
export async function proxy(req: NextRequest) {
  const cookie = req.cookies.get(COOKIE)?.value;
  const valida = cookie ? await sesionValida(cookie) : false;
  const enLogin = req.nextUrl.pathname === "/login";
  if (valida && enLogin) return NextResponse.redirect(new URL("/", req.url));
  if (valida) return;
  const respuesta = enLogin ? NextResponse.next() : NextResponse.redirect(new URL("/login", req.url));
  if (cookie) respuesta.cookies.delete(COOKIE);
  return respuesta;
}

export const config = { matcher: ["/((?!api|_next|favicon.ico).*)"] };
