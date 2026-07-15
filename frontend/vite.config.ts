import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// @vitejs/plugin-react handles TSX. There is no @vitejs/plugin-tsx.
export default defineConfig({
  plugins: [react()],
  // Bind explicitly to 127.0.0.1: 'localhost' resolves to ::1 on Windows,
  // which Playwright's 127.0.0.1 health-poll never sees.
  server: { host: '127.0.0.1', port: 5173, strictPort: true },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
    globals: true,
  },
});
