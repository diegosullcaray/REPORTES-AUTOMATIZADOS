import { NextResponse, type NextRequest } from "next/server";

/** Sin cookie de sesión solo se ve /login; con ella, /login lleva al inicio. La API valida la firma de verdad. */
export function proxy(req: NextRequest) {
  const conSesion = req.cookies.has("reportes_sesion");
  const enLogin = req.nextUrl.pathname === "/login";
  if (!conSesion && !enLogin) return NextResponse.redirect(new URL("/login", req.url));
  if (conSesion && enLogin) return NextResponse.redirect(new URL("/", req.url));
}

export const config = { matcher: ["/((?!api|_next|favicon.ico).*)"] };
