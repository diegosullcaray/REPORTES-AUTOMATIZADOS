import * as React from "react"

const MOBILE_BREAKPOINT = 768
const CONSULTA = `(max-width: ${MOBILE_BREAKPOINT - 1}px)`

// useSyncExternalStore en vez de useEffect + setState (regla react-hooks/set-state-in-effect).
const suscribir = (aviso: () => void) => {
  const mql = window.matchMedia(CONSULTA)
  mql.addEventListener("change", aviso)
  return () => mql.removeEventListener("change", aviso)
}

export function useIsMobile() {
  return React.useSyncExternalStore(suscribir, () => window.matchMedia(CONSULTA).matches, () => false)
}
