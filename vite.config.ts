import { defineConfig, loadEnv } from "vite";
import { resolve, join } from "path";
import tailwindcss from "@tailwindcss/vite";
import { splitVendorChunkPlugin } from 'vite';

export default defineConfig((mode) => {
  const env = loadEnv(mode, process.cwd(), "");
  const isProduction = mode === 'production';

  const CORE_INPUT_DIR = "./apps/core/assets/js";
  const ADVERTISERS_INPUT_DIR = "./apps/advertisers/assets/js";
  const PARTNERS_INPUT_DIR = "./apps/partners/assets/js";
  const MANAGERS_INPUT_DIR = "./apps/managers/assets/js";

  const OUTPUT_DIR = "./static";

  // Функция для группировки входных точек
  const getInputEntries = () => {
    const entries = {
      // Core
      home: join(CORE_INPUT_DIR, "/main/index.js"),
      auth: join(CORE_INPUT_DIR, '/auth/auth.js'),
      
      // Advertiser
      advertiser_dashboard: join(ADVERTISERS_INPUT_DIR, "/dashboard/dashboard.js"),
      advertiser_partners: join(ADVERTISERS_INPUT_DIR, "/partners/partners.js"),
      advertiser_projects: join(ADVERTISERS_INPUT_DIR, "/projects/projects.js"),
      advertiser_requisites: join(ADVERTISERS_INPUT_DIR, "/requisites/requisites.js"),
      advertiser_sales: join(ADVERTISERS_INPUT_DIR, "/sales/sales.js"),
      advertiser_notifications: join(ADVERTISERS_INPUT_DIR, "/notifications/notifications.js"),
      advertiser_settings: join(ADVERTISERS_INPUT_DIR, "/settings/settings.js"),

      // Partner
      partner_dashboard: join(PARTNERS_INPUT_DIR, "/dashboard/dashboard.js"),
      partner_stats: join(PARTNERS_INPUT_DIR, '/stats/stats.js'),
      partner_offers: join(PARTNERS_INPUT_DIR, "/offers/offers.js"),
      partner_connections: join(PARTNERS_INPUT_DIR, "/connections/connections.js"),
      partner_notifications: join(PARTNERS_INPUT_DIR, "/notifications/notifications.js"),
      partner_platforms: join(PARTNERS_INPUT_DIR, "/platforms/platforms.js"),
      partner_links: join(PARTNERS_INPUT_DIR, "/links/links.js"),
      partner_payments: join(PARTNERS_INPUT_DIR, "/payments/payments.js"),
      partner_settings: join(PARTNERS_INPUT_DIR, "/settings/settings.js"),

      // Manager
      manager_dashboard: join(MANAGERS_INPUT_DIR, "/dashboard/dashboard.js"),
      manager_projects: join(MANAGERS_INPUT_DIR, "/projects/projects.js"),
      manager_platforms: join(MANAGERS_INPUT_DIR, "/platforms/platforms.js"),
      manager_users: join(MANAGERS_INPUT_DIR, "/users/users.js"),
      manager_partners: join(MANAGERS_INPUT_DIR, "/partners/partners.js"),
      manager_advertisers: join(MANAGERS_INPUT_DIR, "/advertisers/advertisers.js"),
      manager_reviews: join(MANAGERS_INPUT_DIR, "/reviews/reviews.js"),
      manager_settings: join(MANAGERS_INPUT_DIR, "/settings/settings.js"),
      
      // Static pages
      static_page_core_app: join(CORE_INPUT_DIR, "/static-pages/static_page.js"),
    };

    return entries;
  };

  return {
    base: "/static/",
    build: {
      outDir: resolve(OUTPUT_DIR),
      assetsDir: "",
      manifest: 'manifest.json',
      emptyOutDir: true,
      // Уменьшить использование памяти при сборке
      minify: isProduction ? 'terser' : false,
      cssCodeSplit: true,
      sourcemap: isProduction ? false : 'inline',
      // Отключить отчеты для уменьшения памяти
      reportCompressedSize: false,
      chunkSizeWarningLimit: 1000,
      
      rollupOptions: {
        input: getInputEntries(),
        output: {
          // Оптимизация чанков для уменьшения памяти
          manualChunks(id) {
            if (id.includes('node_modules')) {
              // Разделяем vendor чанки по группам
              if (id.includes('react') || id.includes('react-dom') || id.includes('scheduler')) {
                return 'vendor-react';
              }
              if (id.includes('@reduxjs') || id.includes('redux')) {
                return 'vendor-redux';
              }
              if (id.includes('axios') || id.includes('lodash') || id.includes('moment')) {
                return 'vendor-utils';
              }
              if (id.includes('chart') || id.includes('d3') || id.includes('recharts')) {
                return 'vendor-charts';
              }
              // Остальные зависимости
              return 'vendor-other';
            }
            
            // Разделяем код по приложениям для лучшего кэширования
            if (id.includes('/advertisers/')) {
              return 'chunk-advertiser';
            }
            if (id.includes('/partners/')) {
              return 'chunk-partner';
            }
            if (id.includes('/managers/')) {
              return 'chunk-manager';
            }
            if (id.includes('/core/')) {
              return 'chunk-core';
            }
          },
          // Оптимизация имен файлов
          entryFileNames: isProduction ? 'assets/[name].[hash].js' : 'assets/[name].js',
          chunkFileNames: isProduction ? 'assets/[name].[hash].js' : 'assets/[name].js',
          assetFileNames: isProduction ? 'assets/[name].[hash][extname]' : 'assets/[name][extname]',
        },
        // Ограничиваем параллельную обработку для уменьшения пикового использования памяти
        maxParallelFileOps: isProduction ? 2 : 4,
        // Кэширование для повторных сборок
        cache: true,
      },
    },
    
    // Оптимизация зависимостей
    optimizeDeps: {
      // Включаем только необходимые зависимости
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        // Добавьте сюда другие часто используемые библиотеки
      ],
      exclude: [
        // Исключаем тяжелые библиотеки из предварительной обработки
      ],
      // Отключаем force для dev сервера
      force: false,
    },
    
    resolve: {
      alias: {
        // Алиасы для уменьшения дублирования
        '@core': resolve(CORE_INPUT_DIR),
        '@advertisers': resolve(ADVERTISERS_INPUT_DIR),
        '@partners': resolve(PARTNERS_INPUT_DIR),
        '@managers': resolve(MANAGERS_INPUT_DIR),
      },
      // Оптимизация разрешения модулей
      extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
    },
    
    server: {
      // Оптимизация dev сервера
      hmr: {
        overlay: false, // Отключаем overlay для экономии памяти
      },
      watch: {
        // Используем polling только при необходимости
        usePolling: false,
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/test/**',
          '**/__tests__/**',
        ],
      },
      // Ограничиваем middleware
      middlewareMode: false,
      // Отключаем предзагрузку
      preTransformRequests: false,
      // Увеличиваем таймауты
      open: false,
    },
    
    plugins: [
      tailwindcss(),
      splitVendorChunkPlugin(), // Автоматическое разделение вендор-чанков
    ],
    
    // Оптимизация CSS
    css: {
      devSourcemap: false, // Отключаем sourcemaps в dev
      postcss: {
        plugins: [],
      },
    },
    
    // Увеличиваем лимит памяти для esbuild
    esbuild: {
      logLimit: 10, // Уменьшаем логирование
      drop: isProduction ? ['console', 'debugger'] : [],
    },
  };
});