import { defineConfig } from 'vite';

// Standalone preview, separate from the production application.
export default defineConfig({
  base: './',
  esbuild: { jsx: 'automatic' },
  build: {
    outDir: 'dist-design',
    rollupOptions: { input: 'recallforge-v3.html' },
  },
});
