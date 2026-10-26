import { defineConfig, minimal2023Preset as preset } from '@vite-pwa/assets-generator/config'

// The source icon is full-bleed with the logo inside the safe zone, so no extra padding is needed
export default defineConfig({
  preset: {
    ...preset,
    transparent: { ...preset.transparent, padding: 0 },
    maskable: { ...preset.maskable, padding: 0 },
    apple: { ...preset.apple, padding: 0 },
  },
  images: ['public/icon.svg'],
})
