import { defineConfig, Plugin } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { readdirSync, rmSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

/** Remove stale accessioning entry-point bundles from a previous build. */
function cleanStaleAccessioningAssets(): Plugin {
  return {
    name: 'clean-stale-accessioning-assets',
    buildStart() {
      const assetsDir = resolve(__dirname, '../../static/assets');
      let files: string[];
      try {
        files = readdirSync(assetsDir);
      } catch {
        return; // assets dir not yet created
      }
      for (const file of files) {
        // Match entry bundles only — skip chunk files
        if (/^accessioning-(?!chunk)[^.]+\.(js|css)$/.test(file)) {
          rmSync(resolve(assetsDir, file));
          console.log(`[clean] Removed stale accessioning asset: ${file}`);
        }
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), cleanStaleAccessioningAssets()],
  build: {
    outDir: '../../static',
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/accessioning-[hash].js',
        chunkFileNames: 'assets/accessioning-chunk-[hash].js',
        assetFileNames: 'assets/accessioning-[hash][extname]',
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
