import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  root: 'frontend',
  base: '/static/v2/',
  plugins: [react()],
  build: {
    outDir: '../web_app/static/v2',
    emptyOutDir: true
  }
});
