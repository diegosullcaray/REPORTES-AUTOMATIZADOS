/** Responsables cuyos reportes mensuales se validan. Módulo plano (sin "use client"): lo leen páginas de servidor y componentes. */
export const GRUPOS = { piero: "Heredados de Piero", erick: "Heredados de Erick" } as const;
export type Grupo = keyof typeof GRUPOS;
