import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

// https://vite.dev/config/
export default defineConfig(async () => ({
  plugins: [react()],

  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  //
  // 1. prevent Vite from obscuring rust errors
  clearScreen: false,
  // 2. tauri expects a fixed port, fail if that port is not available
  server: {
    port: 1431, // Changed from 1430 to 1431 to avoid port conflict
    strictPort: true,
    host: host || false,
    // Dev proxy: forward some backend endpoints to local dev servers
    proxy: process.env.NODE_ENV !== 'production' ? {
      '/api/kube': {
        target: process.env.KUBEC_SERVER_URL || 'http://localhost:51821',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/kube/, '/api/kube'),
      },
      // LLM pool & agent endpoints -> backend FastAPI (127.0.0.1:8000)
      '/llm_pool': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/llm_pool/, '/llm_pool'),
      },
      '/llm_auth': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/llm_auth/, '/llm_auth'),
      },
      '/llm_config': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/llm_config/, '/llm_config'),
      },
      '/agent': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/agent/, '/agent'),
      },
      '/build': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/build/, '/build'),
      },
      '/api/snapshots': {
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/snapshots/, '/snapshots'),
      },
    } : undefined,
    hmr: host
      ? {
          protocol: "ws",
          host,
          port: 1432, // HMR port incremented as well
        }
      : undefined,
    watch: {
      // 3. tell Vite to ignore watching `src-tauri`
      ignored: ["**/src-tauri/**"],
    },
  },
}));
