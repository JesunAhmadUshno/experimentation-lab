import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads ../results/*.json at build time, so every number on the page is generated, never typed.
export default defineConfig({
  base: '/experimentation-lab/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
});
