---
name: web-diseno-dokploy
description: Estética y patrones de interfaz copiados de Dokploy para la web de reportes. Usar al crear o cambiar cualquier pantalla.
---

# Diseño al estilo Dokploy

Referencia local: `C:\Users\24681\Videos\DD\referencias\dokploy\apps\dokploy\components`.

- **Color solo por token** `--mis-*` o clases de shadcn; nada de hex.
- **Plano**: sin vidrio ni wallpaper. Sección = `components/marco.tsx`; tarjeta = `components/tarjeta.tsx`.
- **Detalle de un servicio** (reporte): encabezado con ícono + estado, insignias y pestañas en la URL (`?tab=`).
- **Logs y detalle van juntos en un diálogo** (como `ShowDeployment`): datos, terminal en vivo y archivos; no en columnas ni en otra página.
- **Vista previa de archivos en diálogo**, nunca en dos columnas.
- **Acceso**: `components/layout-acceso.tsx` (panel de marca a la izquierda, formulario centrado) como el `OnboardingLayout` de Dokploy.
- **Estados en orden**: error → cargando (esqueleto) → vacío → contenido (`components/estados.tsx`). Avisos con `toast`.
- Móvil primero; las listas que cambian se refrescan solas (5–10 s).
