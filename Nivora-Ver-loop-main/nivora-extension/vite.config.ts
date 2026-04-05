import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-manifest',
      writeBundle() {
        // Manifest is already handled by public folder
      }
    }
  ],
  build: {
    outDir: 'dist',
    sourcemap: false, // Disable sourcemaps for extensions
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'index.html'),
      },
      output: {
        entryFileNames: 'assets/[name].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    },
    // Keep assets separate (don't inline) to avoid CSP issues
    assetsInlineLimit: 0,
  },
  // Use relative paths for extension compatibility
  base: './',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  // Optimize for extensions
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
  },
})
