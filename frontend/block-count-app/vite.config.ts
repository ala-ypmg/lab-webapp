import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../../static',
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/ypb-[hash].js',
        chunkFileNames: 'assets/ypb-chunk-[hash].js',
        assetFileNames: 'assets/ypb-[hash][extname]',
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/setupTests.ts',
        '**/*.d.ts',
        '**/*.config.*',
        '**/index.ts',
      ],
    },
  },
});
