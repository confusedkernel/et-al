import type { NextConfig } from "next";

// In production Caddy routes /api/* straight to the backend; this rewrite covers `pnpm dev`.
const apiUrl = process.env.API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
  },
};

export default nextConfig;
