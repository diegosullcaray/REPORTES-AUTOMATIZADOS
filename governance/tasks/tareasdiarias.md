# Especificación de Interfaz de Usuario: Panel de Reportes Automatizados

## 1. Visión General y Estilo Visual (Inspiración: Dokploy)
Refactorizar el frontend de la aplicación (Next.js, Tailwind CSS, shadcn/ui) para adoptar una estética minimalista, limpia y enfocada en el desarrollador, similar a **Dokploy**.

**Reglas de Diseño:**
- **Esquema de colores:** Alto contraste en dark mode, fondos sutiles (`bg-background` y `bg-muted/30` para sidebars/paneles), bordes delicados (`border-border`).
- **Tipografía:** Limpia (Inter o Geist), pesos de fuente consistentes. Textos secundarios en `text-muted-foreground`.
- **Botones e Inputs:** Estilo plano, bordes redondeados (radius estándar de shadcn), efectos `hover` sutiles. Sin sombras excesivas.
- **Iconografía:** Usar `lucide-react`.

## 2. Arquitectura de Navegación (shadcn/ui)

### 2.1. Sidebars Retráctiles (Doble Sidebar)
Implementar el nuevo componente `<Sidebar>` de shadcn/ui.
- **Sidebar Primario (Izquierda - Global):** Debe ser **retráctil**. Contiene la navegación principal de la app:
  - 📊 Reportes
  - ⏱️ Ejecuciones
  - ⚙️ Configuración (Reemplaza a "Conexiones")
- **Sidebar Secundario (Izquierda/Interno - Contextual):** Debe ser **retráctil**. Aparece únicamente cuando se entra al módulo de "Reportes". Funciona como un explorador de archivos o lista de reportes disponibles organizados por categoría (Diarios, Mensuales). 

### 2.2. Header y Breadcrumbs
- En la parte superior del contenido principal, fijar un header con un botón `SidebarTrigger` para colapsar/expandir el sidebar.
- Acompañar el header con el componente `<Breadcrumb>` de shadcn/ui. Debe ser dinámico y reflejar la ruta actual (ej. `Reportes > Diarios > Cartera sin asignar`).

## 3. Limpieza y Refactorización de Vistas

### 3.1. Panel de Reportes (Vista Limpia)
Eliminar toda la sobrecarga de información y "ruido" visual innecesario en la vista de detalle del reporte.
- **ELIMINAR:** Etiquetas redundantes, descripciones largas y datos irrelevantes para la ejecución (Ej: quitar *"Cartera sin asignar (diario): cartera por sectorista/territorio sin asignación"*, *"Diarias 02"*, *"diaria"*, *"servidor mish"*, *"envía correo"*).
- **MANTENER (Estilo Dokploy):** 
  - Un encabezado limpio con el título del reporte ("Cartera sin Asignar").
  - Un badge sutil indicando el tipo ("Diario").
  - Parámetros de ejecución (ej. Selector de fecha de corte).
  - Un botón de acción principal ("▶ Ejecutar Reporte") y un log tipo terminal/consola para ver el resultado en tiempo real.

### 3.2. Módulo de Configuración (Reemplaza "Conexiones")
- Eliminar la ruta y vista aislada de `app/conexiones`.
- Crear una nueva ruta `app/configuracion`.
- Esta vista debe actuar como un panel de control general al estilo Dokploy (Tabs horizontales o menú vertical simple).
- **Sección de Base de Datos:** Mover toda la lógica de validación de conexiones (Testing de bases de datos, credenciales y servidores) dentro de este módulo bajo la pestaña/sección "Bases de Datos". Debe incluir un botón para hacer "Ping" o "Test de Conexión" que devuelva un Toast de éxito/error.

## 4. Estructura de Componentes Esperada

Adapta el código para usar el ecosistema shadcn/ui:
```tsx
// Ejemplo estructural para el layout principal usando el AppSidebar
<SidebarProvider>
  <AppSidebar/>          {/* Sidebar Primario retráctil */}
  <SidebarInset>
    <Header>
      <SidebarTrigger/>  {/* Botón para retraer */}
      <Breadcrumbs/>     {/* shadcn Breadcrumbs */}
    </Header>
    <main>
      {/* Contenido principal. Si estamos en Reportes, puede tener su propio Sidebar secundario para la lista */}
      {children}
    </main>
  </SidebarInset>
</SidebarProvider>