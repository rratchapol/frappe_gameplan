import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import path from 'path'
import { existsSync, readdirSync } from 'node:fs'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig(async ({ mode }) => {
  const isDev = mode === 'development'

  // Setup local frappe-ui for development
  const localFrappeUIPath = path.resolve(__dirname, '../frappe-ui')
  const useLocalFrappeUI = isDev && existsSync(path.join(localFrappeUIPath, 'node_modules'))

  if (isDev && existsSync(localFrappeUIPath) && !useLocalFrappeUI) {
    console.warn('⚠️  Local frappe-ui found but dependencies not installed.')
    console.warn('   Run: cd ../frappe-ui && yarn install')
  }

  const frappeui = await importFrappeUIPlugin(useLocalFrappeUI)

  // Base aliases shared across all modes
  const baseAliases = {
    '@': path.resolve(__dirname, 'src'),
    'tailwind.config.js': path.resolve(__dirname, 'tailwind.config.js'),
  }

  // Local frappe-ui aliases for development
  const localFrappeUIAliases = useLocalFrappeUI
    ? {
        // CSS alias must come before general alias for proper resolution
        'frappe-ui/style.css': path.resolve(localFrappeUIPath, 'src', 'style.css'),
        'frappe-ui': localFrappeUIPath,
      }
    : {}

  return {
    define: {
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
    },
    plugins: [
      frappeui({
        frappeProxy: true,
        lucideIcons: true,
        jinjaBootData: true,
        frappeTypes: {
          input: {
            gameplan: [
              'gp_project',
              'gp_member',
              'gp_team',
              'gp_comment',
              'gp_discussion',
              'gp_page',
              'gp_task',
              'gp_poll',
              'gp_guest_access',
              'gp_invitation',
              'gp_user_profile',
              'gp_notification',
              'gp_activity',
              'gp_search_feedback',
              'gp_draft',
              'gp_tag',
              'gp_pinned_project',
            ],
          },
        },
        buildConfig: {
          indexHtmlPath: '../gameplan/www/g.html',
        },
      }),
      vue(),
      vueJsx(),
      visualizer({ emitFile: true }),
    ],
    server: {
      allowedHosts: true,
      fs: {
        allow: [
          // Allow serving files from project root, node_modules, and frappe-ui. To fix the error:
          // The request url "~/frappe-bench/apps/gameplan/frappe-ui/src/fonts/Inter/Inter-Medium.woff2" is outside of Vite serving allow list.
          '..',
          'node_modules',
          '../frappe-ui',
        ],
      },
    },
    resolve: {
      alias: {
        ...localFrappeUIAliases,
        ...baseAliases,
        // TipTap aliases to prevent duplicate instances when using local frappe-ui
        ...getTipTapAliases(useLocalFrappeUI, localFrappeUIPath),
      },
    },
    optimizeDeps: {
      include: ['feather-icons', 'tailwind.config.js'],
    },
  }
})

/**
 * Get TipTap package aliases to prevent duplicate instances
 * when using local frappe-ui alongside gameplan's node_modules
 */
function getTipTapAliases(useLocalFrappeUI, localFrappeUIPath) {
  if (!useLocalFrappeUI) return {}

  const gameplanTiptap = path.join(__dirname, 'node_modules/@tiptap')
  const frappeUITiptap = path.join(localFrappeUIPath, 'node_modules/@tiptap')

  if (!existsSync(gameplanTiptap) || !existsSync(frappeUITiptap)) {
    return {}
  }

  const commonPackages = readdirSync(gameplanTiptap).filter((pkg) =>
    readdirSync(frappeUITiptap).includes(pkg),
  )

  return Object.fromEntries(
    commonPackages.map((pkg) => [`@tiptap/${pkg}`, path.join(gameplanTiptap, pkg)]),
  )
}

/**
 * Import frappe-ui Vite plugin from local copy or npm package
 */
async function importFrappeUIPlugin(useLocal) {
  const modulePath = useLocal ? '../frappe-ui/vite/index.js' : 'frappe-ui/vite'

  try {
    return (await import(modulePath)).default
  } catch (error) {
    if (useLocal) {
      console.warn('⚠️  Failed to import local frappe-ui plugin, falling back to npm package')
      console.warn('   Error:', error.message)
      return (await import('frappe-ui/vite')).default
    }
    throw error
  }
}
