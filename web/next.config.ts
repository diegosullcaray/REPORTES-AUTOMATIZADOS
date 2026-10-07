import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // La API de Python solo escucha en local; el navegador la ve como /api (mismo origen, sin CORS).
  async rewrites() {
    return [{ source: "/api/:ruta*", destination: `${process.env.REPORTES_API_URL ?? "http://127.0.0.1:8000"}/api/:ruta*` }];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
