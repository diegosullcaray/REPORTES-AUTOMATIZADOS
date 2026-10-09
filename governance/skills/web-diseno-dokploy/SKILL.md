---
name: web-diseno-dokploy
description: Estética y patrones de interfaz copiados de Dokploy para la web de reportes. Usar al crear o cambiar cualquier pantalla.
---

# Diseño al estilo Dokploy

Referencia local: `C:\Users\24681\Videos\DD\referencias\dokploy\apps\dokploy\components`.

- **Color solo por token** `--mis-*` o clases de shadcn; nada de hex ni de paleta cruda de Tailwind (`bg-red-500`). `frontend/src/lib/colores.test.ts` lo vigila.
- **Reglas de color sacadas del análisis de MIS** (`MIS-angular-front/src/app/theme/tokens.css`, copia idéntica en `frontend/src/app/tokens.css`):
  - La marca como **texto o ícono** es `--mis-primary-text` (se aclara en oscuro: 9.3:1); `--mis-primary` es un **fondo sólido** con `--mis-text-on-primary`. No uses `text-primary` para texto.
  - `--mis-text-tertiary` da 3.0:1 en claro: solo decorativo, nunca texto informativo (usa `--mis-text-secondary`, 5.1:1).
  - Estados con `--mis-success|warning|danger` y su `-light` como fondo (≥ 4.5:1 en los dos temas).
  - Velo y sombra de diálogos: `--mis-dialog-mask` y `--mis-shadow-lg`, no negro fijo.
  - La consola usa los valores de `.dark` de MIS en los dos temas (`--terminal-*` en `globals.css`).
- **Plano**: sin vidrio ni wallpaper. Sección = `components/marco.tsx`; tarjeta = `components/tarjeta.tsx`.
- **Detalle de un servicio** (reporte): encabezado con ícono + estado, insignias y pestañas en la URL (`?tab=`).
- **Logs y detalle van juntos en un diálogo** (como `ShowDeployment`): datos, terminal en vivo y archivos; no en columnas ni en otra página.
- **Vista previa de archivos en diálogo**, nunca en dos columnas.
- **Acceso**: `components/layout-acceso.tsx` (panel de marca a la izquierda, formulario centrado) como el `OnboardingLayout` de Dokploy.
- **Estados en orden**: error → cargando (esqueleto) → vacío → contenido (`components/estados.tsx`). Avisos con `toast`.
- Móvil primero; las listas que cambian se refrescan solas (5–10 s).
