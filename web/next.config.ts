import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',
  
  // Disable source maps in production for smaller builds
  productionBrowserSourceMaps: false,
  
  // Disable ESLint during build for demo purposes
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Disable TypeScript checking during build (we can enable later)
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Disable telemetry
  telemetry: false,
  
  // Pass through environment variables
  env: {
    NEXT_PUBLIC_APP_MODE: process.env.NEXT_PUBLIC_APP_MODE || 'production',
  },
};

export default nextConfig;
