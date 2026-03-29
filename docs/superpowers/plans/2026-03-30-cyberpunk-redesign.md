# Cyberpunk Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Full-site cyberpunk visual redesign of the Game Boosting Platform frontend, preserving all functionality and page structure.

**Architecture:** CSS-first approach using Tailwind config extension + main.css component classes. Each Vue page gets class replacements and minor template additions (decorative elements, images). No JS logic changes. Centralized game image data module for DRY image references across pages.

**Tech Stack:** Tailwind CSS 3.4, Vue 3 SFC templates, inline SVG assets, external image URLs

**Spec:** `docs/superpowers/specs/2026-03-30-cyberpunk-redesign-design.md`

---

## File Structure

### Modified files
- `frontend/tailwind.config.js` — extended colors, animations, keyframes
- `frontend/src/assets/main.css` — new/modified component + utility classes
- `frontend/src/App.vue` — nav bar cyberpunk styling (151 lines)
- `frontend/src/views/HomeView.vue` — full hero + game showcase redesign (403 lines)
- `frontend/src/views/LoginView.vue` — cyberpunk form styling (178 lines)
- `frontend/src/views/RegisterView.vue` — mirror of login styling (221 lines)
- `frontend/src/views/OrderList.vue` — order cards + filters (397 lines)
- `frontend/src/views/OrderCreate.vue` — AI step + form (411 lines)
- `frontend/src/views/OrderDetail.vue` — timeline + hero (328 lines)
- `frontend/src/views/ProfileView.vue` — profile + booster app (380 lines)
- `frontend/src/views/AdminView.vue` — admin dashboard (398 lines)
- `frontend/src/views/NotFound.vue` — 404 page (25 lines)

### New files
- `frontend/src/assets/images/ui/cyber-grid.svg` — grid texture
- `frontend/src/assets/images/ui/scanline.svg` — scanline texture
- `frontend/src/assets/images/ui/noise.svg` — noise grain texture
- `frontend/src/data/gameImages.js` — centralized game image URLs and metadata

---

## Task 1: Tailwind Config — Colors, Animations, Keyframes

**Files:**
- Modify: `frontend/tailwind.config.js`

- [ ] **Step 1: Extend color palette and animations**

Replace the entire content of `frontend/tailwind.config.js` with:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        neon: {
          pink: '#ff2d6b',
          'pink-light': '#ff6b9d',
          purple: '#b829dd',
          'purple-light': '#d946ef',
          blue: '#00f0ff',
        },
        dark: {
          base: '#0a0a0f',
          surface: '#12121a',
          elevated: '#1a1a2e',
        },
      },
      boxShadow: {
        glow: '0 18px 45px rgba(6, 182, 212, 0.28)',
        'glow-neon': '0 0 20px rgba(0, 240, 255, 0.3)',
        'glow-pink': '0 0 20px rgba(255, 45, 107, 0.3)',
        'glow-purple': '0 0 20px rgba(184, 41, 221, 0.3)',
        panel: '0 24px 70px rgba(2, 6, 23, 0.42)',
      },
      animation: {
        float: 'float 7s ease-in-out infinite',
        'fade-up': 'fadeUp 0.7s ease-out both',
        'pulse-soft': 'pulse 2.4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        glitch: 'glitch 2s infinite',
        'glitch-once': 'glitch 0.8s ease-out 1',
        'scanline-move': 'scanlineMove 8s linear infinite',
        'neon-pulse': 'neonPulse 2s ease-in-out infinite',
        'flow-line': 'flowLine 3s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
        scanlineMove: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        neonPulse: {
          '0%, 100%': { boxShadow: '0 0 15px rgba(0, 240, 255, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(0, 240, 255, 0.6)' },
        },
        flowLine: {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '200% 0%' },
        },
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 2: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/tailwind.config.js
git commit -m "feat(frontend): extend tailwind config with cyberpunk colors and animations"
```

---

## Task 2: Main CSS — Cyberpunk Component Classes

**Files:**
- Modify: `frontend/src/assets/main.css`

- [ ] **Step 1: Update base layer with cyberpunk body styling**

Replace the `body` rule and its `::before`/`::after` pseudo-elements in the `@layer base` section (lines 14-47) with:

```css
  body {
    @apply min-h-screen bg-dark-base text-slate-100 antialiased;
    font-family: "HarmonyOS Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
    background-image:
      radial-gradient(circle at top left, rgba(0, 240, 255, 0.12), transparent 34%),
      radial-gradient(circle at top right, rgba(184, 41, 221, 0.10), transparent 28%),
      linear-gradient(180deg, #0a0a0f 0%, #0d0d1a 42%, #0a0a0f 100%);
    position: relative;
  }

  body::before,
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: -1;
  }

  body::before {
    background-image:
      radial-gradient(circle at 20% 20%, rgba(0, 240, 255, 0.06), transparent 24%),
      radial-gradient(circle at 80% 12%, rgba(255, 45, 107, 0.05), transparent 22%),
      radial-gradient(circle at 50% 88%, rgba(184, 41, 221, 0.08), transparent 26%);
    filter: blur(8px);
  }

  body::after {
    background-image:
      linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
    background-size: 72px 72px;
    mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.35), transparent 82%);
  }
```

- [ ] **Step 2: Update scrollbar styles**

Replace the scrollbar rules (lines 62-77) with:

```css
  ::-webkit-scrollbar {
    @apply w-2;
  }

  ::-webkit-scrollbar-track {
    background: #0a0a0f;
  }

  ::-webkit-scrollbar-thumb {
    @apply rounded-full;
    background: linear-gradient(180deg, #0891b2, #b829dd);
  }

  ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #22d3ee, #d946ef);
  }
```

- [ ] **Step 3: Update existing component classes in @layer components**

Replace the following existing component classes:

**`.hero-panel`** — replace with:
```css
  .hero-panel {
    @apply relative overflow-hidden border border-white/10 bg-dark-surface/75 shadow-panel backdrop-blur-xl;
    border-radius: 28px;
    border-image: linear-gradient(135deg, rgba(0,240,255,0.3), transparent 40%, rgba(255,45,107,0.3)) 1;
    border-image-slice: 1;
    border-style: solid;
    border-width: 1px;
  }
```

Wait — `border-image` doesn't work with `border-radius`. Use a different approach:

```css
  .hero-panel {
    @apply relative overflow-hidden rounded-[28px] bg-dark-surface/75 shadow-panel backdrop-blur-xl;
    border: 1px solid rgba(0, 240, 255, 0.15);
  }

  .hero-panel::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(135deg, rgba(0,240,255,0.4), transparent 40%, rgba(255,45,107,0.3));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    z-index: 1;
  }
```

**`.surface-card`** — replace with:
```css
  .surface-card {
    @apply rounded-[28px] bg-dark-surface/65 shadow-panel backdrop-blur-xl;
    border: 1px solid rgba(0, 240, 255, 0.1);
    position: relative;
  }

  .surface-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 40px;
    height: 2px;
    background: linear-gradient(90deg, #00f0ff, transparent);
    border-radius: 0 0 2px 0;
    z-index: 1;
  }
```

**`.card-hover`** — replace with:
```css
  .card-hover {
    @apply card transition-all duration-300;
  }

  .card-hover:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 240, 255, 0.3);
    box-shadow: 0 8px 30px rgba(0, 240, 255, 0.15);
  }
```

**`.btn-primary`** — replace with:
```css
  .btn-primary {
    @apply btn text-white font-bold shadow-glow-neon;
    background: linear-gradient(135deg, #06b6d4 0%, #b829dd 100%);
    clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
  }

  .btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.4);
  }
```

**`.btn-secondary`** — replace with:
```css
  .btn-secondary {
    @apply btn bg-transparent text-white;
    border: 1px dashed rgba(255, 45, 107, 0.5);
  }

  .btn-secondary:hover {
    background: rgba(255, 45, 107, 0.1);
    border-color: rgba(255, 45, 107, 0.8);
  }
```

**`.btn-ghost`** — replace with:
```css
  .btn-ghost {
    @apply btn border border-transparent bg-transparent text-slate-300;
  }

  .btn-ghost:hover {
    @apply border-white/10 text-white;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 240, 255, 0.03) 2px,
      rgba(0, 240, 255, 0.03) 4px
    );
  }
```

**`.btn-danger`** — replace with:
```css
  .btn-danger {
    @apply btn text-white focus:ring-pink-400/60;
    background: #ff2d6b;
  }

  .btn-danger:hover {
    animation: glitch 0.3s ease-out 1;
    background: #ff6b9d;
  }
```

**`.btn-success`** — replace with:
```css
  .btn-success {
    @apply btn bg-emerald-500 text-slate-950 focus:ring-emerald-400/60;
  }

  .btn-success:hover {
    @apply bg-emerald-400;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
  }
```

**`.input`** — replace with:
```css
  .input {
    @apply w-full rounded-2xl bg-dark-surface px-4 py-3 text-sm text-white placeholder:text-slate-500;
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.2s ease;
  }

  .input:focus {
    outline: none;
    border-color: rgba(0, 240, 255, 0.5);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    background: #1a1a2e;
  }
```

**`.input-error`** — replace with:
```css
  .input-error {
    border-color: rgba(255, 45, 107, 0.5) !important;
  }

  .input-error:focus {
    border-color: rgba(255, 45, 107, 0.7) !important;
    box-shadow: 0 0 15px rgba(255, 45, 107, 0.2) !important;
  }
```

**`.nav-chip-active`** — replace with:
```css
  .nav-chip-active {
    @apply nav-chip font-semibold;
    background: rgba(0, 240, 255, 0.15);
    color: #00f0ff;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
  }
```

**`.nav-chip-idle`** — replace with:
```css
  .nav-chip-idle {
    @apply nav-chip text-slate-400;
  }

  .nav-chip-idle:hover {
    @apply text-white;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 240, 255, 0.04) 2px,
      rgba(0, 240, 255, 0.04) 4px
    );
  }
```

**Status badges** — replace all badge classes with:
```css
  .badge-pending {
    @apply badge border-amber-400/30 bg-amber-400/10 text-amber-200;
    animation: neonPulse 2s ease-in-out infinite;
    --tw-shadow-color: rgba(251, 191, 36, 0.15);
  }

  .badge-locked {
    @apply badge text-cyan-200;
    border-color: rgba(0, 240, 255, 0.3);
    background:
      repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0, 240, 255, 0.05) 3px, rgba(0, 240, 255, 0.05) 4px),
      rgba(0, 240, 255, 0.1);
  }

  .badge-completed {
    @apply badge border-emerald-400/30 bg-emerald-400/10 text-emerald-200;
  }

  .badge-disputed {
    @apply badge text-white;
    background: rgba(255, 45, 107, 0.2);
    border-color: rgba(255, 45, 107, 0.4);
    animation: glitch 2s infinite;
  }

  .badge-cancelled {
    @apply badge border-slate-400/20 bg-slate-400/10 text-slate-400;
  }

  .badge-approved {
    @apply badge border-emerald-400/30 bg-emerald-400/10 text-emerald-200;
  }

  .badge-rejected {
    @apply badge text-white;
    background: rgba(255, 45, 107, 0.15);
    border-color: rgba(255, 45, 107, 0.3);
  }

  .badge-review {
    @apply badge;
    border-color: rgba(0, 240, 255, 0.3);
    background: rgba(0, 240, 255, 0.1);
    color: #67e8f9;
  }
```

**`.stat-card`** — replace with:
```css
  .stat-card {
    @apply p-4 shadow-lg;
    border-radius: 20px;
    border: 1px solid rgba(0, 240, 255, 0.1);
    background: rgba(18, 18, 26, 0.6);
  }
```

**`.empty-panel`** — replace with:
```css
  .empty-panel {
    @apply rounded-[28px] p-10 text-center text-slate-400;
    border: 1px dashed rgba(0, 240, 255, 0.15);
    background: rgba(18, 18, 26, 0.45);
  }
```

**Message classes** — replace with:
```css
  .message-success {
    @apply rounded-2xl px-4 py-3 text-sm text-emerald-200;
    border: 1px solid rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.1);
  }

  .message-error {
    @apply rounded-2xl px-4 py-3 text-sm;
    color: #ff6b9d;
    border: 1px solid rgba(255, 45, 107, 0.3);
    background: rgba(255, 45, 107, 0.1);
  }

  .message-info {
    @apply rounded-2xl px-4 py-3 text-sm;
    color: #67e8f9;
    border: 1px solid rgba(0, 240, 255, 0.3);
    background: rgba(0, 240, 255, 0.1);
  }
```

- [ ] **Step 4: Add new cyberpunk utility classes in @layer utilities**

Add these after the existing `.text-gradient` class:

```css
  .cyber-gradient {
    background-image: linear-gradient(135deg, #00f0ff 0%, #b829dd 50%, #ff2d6b 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }

  .neon-text {
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3);
  }

  .neon-text-amber {
    text-shadow: 0 0 10px rgba(251, 191, 36, 0.5), 0 0 20px rgba(251, 191, 36, 0.3);
  }

  .neon-text-pink {
    text-shadow: 0 0 10px rgba(255, 45, 107, 0.5), 0 0 20px rgba(255, 45, 107, 0.3);
  }

  .cyber-divider {
    height: 1px;
    background: linear-gradient(90deg, #00f0ff, transparent 50%, #ff2d6b);
    border: none;
  }

  .cyber-corner {
    position: relative;
  }

  .cyber-corner::before,
  .cyber-corner::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    pointer-events: none;
    z-index: 2;
  }

  .cyber-corner::before {
    top: -1px;
    left: -1px;
    border-top: 2px solid #00f0ff;
    border-left: 2px solid #00f0ff;
  }

  .cyber-corner::after {
    bottom: -1px;
    right: -1px;
    border-bottom: 2px solid #ff2d6b;
    border-right: 2px solid #ff2d6b;
  }

  .clip-angle-sm {
    clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
  }

  .clip-angle-lg {
    clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px));
  }

  .scanline-overlay {
    position: relative;
  }

  .scanline-overlay::after {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 2;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0, 240, 255, 0.02) 2px,
      rgba(0, 240, 255, 0.02) 4px
    );
    border-radius: inherit;
  }

  .glitch-text {
    position: relative;
    display: inline-block;
  }

  .glitch-text::before,
  .glitch-text::after {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }

  .glitch-text::before {
    color: #00f0ff;
    animation: glitch 2s infinite;
    clip-path: polygon(0 0, 100% 0, 100% 35%, 0 35%);
    transform: translate(-2px);
    opacity: 0.7;
  }

  .glitch-text::after {
    color: #ff2d6b;
    animation: glitch 2s infinite reverse;
    clip-path: polygon(0 65%, 100% 65%, 100% 100%, 0 100%);
    transform: translate(2px);
    opacity: 0.7;
  }

  .status-line-pending {
    border-left: 2px solid #fbbf24;
  }

  .status-line-locked {
    border-left: 2px solid #00f0ff;
  }

  .status-line-completed {
    border-left: 2px solid #10b981;
  }

  .status-line-disputed {
    border-left: 2px solid #ff2d6b;
  }

  .status-line-cancelled {
    border-left: 2px solid #64748b;
  }
```

- [ ] **Step 5: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/assets/main.css
git commit -m "feat(frontend): add cyberpunk component and utility classes"
```

---

## Task 3: UI Texture Assets

**Files:**
- Create: `frontend/src/assets/images/ui/cyber-grid.svg`
- Create: `frontend/src/assets/images/ui/scanline.svg`
- Create: `frontend/src/assets/images/ui/noise.svg`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p "e:/game-boosting-platform/frontend/src/assets/images/ui"
mkdir -p "e:/game-boosting-platform/frontend/src/assets/images/games"
```

- [ ] **Step 2: Create cyber-grid.svg**

Write to `frontend/src/assets/images/ui/cyber-grid.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72">
  <defs>
    <pattern id="grid" width="72" height="72" patternUnits="userSpaceOnUse">
      <path d="M 72 0 L 0 0 0 72" fill="none" stroke="rgba(0,240,255,0.06)" stroke-width="0.5"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
</svg>
```

- [ ] **Step 3: Create scanline.svg**

Write to `frontend/src/assets/images/ui/scanline.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="4">
  <rect width="100" height="1" fill="rgba(0,240,255,0.03)"/>
  <rect y="2" width="100" height="1" fill="rgba(0,240,255,0.02)"/>
</svg>
```

- [ ] **Step 4: Create noise.svg**

Write to `frontend/src/assets/images/ui/noise.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#noise)" opacity="0.04"/>
</svg>
```

- [ ] **Step 5: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/assets/images/
git commit -m "feat(frontend): add cyberpunk UI texture SVG assets"
```

---

## Task 4: Game Image Data Module

**Files:**
- Create: `frontend/src/data/gameImages.js`

- [ ] **Step 1: Create game images data module**

Write to `frontend/src/data/gameImages.js`:

```js
/**
 * Centralized game image data.
 * Hero images are external URLs (lazy loaded with fallback).
 * Logos reference local SVG placeholders or can be swapped for PNGs.
 */

export const GAME_IMAGES = {
  '王者荣耀': {
    hero: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&q=80',
    color: '#ff6b2b',
    gradient: 'from-orange-500/20 to-red-600/20',
  },
  '英雄联盟': {
    hero: 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&q=80',
    color: '#00a3ff',
    gradient: 'from-blue-500/20 to-cyan-600/20',
  },
  '和平精英': {
    hero: 'https://images.unsplash.com/photo-1552820728-8b83bb6b2b28?w=800&q=80',
    color: '#f5c518',
    gradient: 'from-yellow-500/20 to-amber-600/20',
  },
  '原神': {
    hero: 'https://images.unsplash.com/photo-1618336753974-aae8e04506aa?w=800&q=80',
    color: '#a78bfa',
    gradient: 'from-violet-500/20 to-purple-600/20',
  },
  '永劫无间': {
    hero: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&q=80',
    color: '#ef4444',
    gradient: 'from-red-500/20 to-rose-600/20',
  },
}

/** External background images for non-game pages */
export const PAGE_BACKGROUNDS = {
  hero: 'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1600&q=80',
  login: 'https://images.unsplash.com/photo-1633259584604-afdc243122ea?w=1600&q=80',
  register: 'https://images.unsplash.com/photo-1633259584604-afdc243122ea?w=1600&q=80',
  notFound: 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1600&q=80',
}

/**
 * Get game image data by game name. Returns fallback if not found.
 */
export function getGameImage(gameName) {
  return GAME_IMAGES[gameName] || {
    hero: null,
    color: '#00f0ff',
    gradient: 'from-cyan-500/20 to-blue-600/20',
  }
}

/**
 * Handle image load error by setting a gradient fallback.
 * Usage: <img @error="onImgError($event)" />
 */
export function onImgError(event) {
  const el = event.target
  el.style.display = 'none'
  if (el.parentElement) {
    el.parentElement.style.background = 'linear-gradient(135deg, #12121a, #1a1a2e)'
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/data/gameImages.js
git commit -m "feat(frontend): add centralized game image data module"
```

---

## Task 5: App.vue — Navigation Bar Redesign

**Files:**
- Modify: `frontend/src/App.vue` (151 lines)

- [ ] **Step 1: Update nav bar styling**

In `App.vue`, find the `<nav>` element (around line 3):

```html
<nav class="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
```

Replace with:

```html
<nav class="sticky top-0 z-50 bg-dark-base/80 backdrop-blur-xl" style="border-bottom: 1px solid transparent; border-image: linear-gradient(90deg, rgba(0,240,255,0.3), transparent 50%, rgba(255,45,107,0.3)) 1;">
```

- [ ] **Step 2: Update logo text with glitch effect**

Find the logo text element (the `<span>` or heading containing "游戏代练平台"). Add the glitch-once animation class:

Find:
```html
<span class="text-lg font-bold text-white">游戏代练平台</span>
```

Replace with:
```html
<span class="text-lg font-bold animate-glitch-once" style="color: #00f0ff; text-shadow: 0 0 10px rgba(0,240,255,0.5);">游戏代练平台</span>
```

- [ ] **Step 3: Update footer styling**

Find the `<footer>` element:

```html
<footer class="border-t border-white/10 bg-slate-950/70">
```

Replace with:

```html
<footer class="bg-dark-base/70" style="border-top: 1px solid transparent; border-image: linear-gradient(90deg, rgba(0,240,255,0.3), transparent 50%, rgba(255,45,107,0.3)) 1;">
```

- [ ] **Step 4: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/App.vue
git commit -m "feat(frontend): apply cyberpunk styling to nav bar and footer"
```

---

## Task 6: HomeView — Hero + Game Showcase Redesign

**Files:**
- Modify: `frontend/src/views/HomeView.vue` (403 lines)

This is the largest page change. Key modifications:

- [ ] **Step 1: Add game images import**

In the `<script setup>` section, add at the top after existing imports:

```js
import { GAME_IMAGES, PAGE_BACKGROUNDS, onImgError } from '@/data/gameImages.js'
```

- [ ] **Step 2: Update hero section**

Find the hero `<section>` and update its classes and content. The hero section should have a background image with overlay:

Find the hero section opening tag (around line with `hero-panel`):
```html
<section class="hero-panel p-6 sm:p-8 lg:p-10">
```

Replace with:
```html
<section class="hero-panel scanline-overlay p-6 sm:p-8 lg:p-10" style="background-image: linear-gradient(135deg, rgba(10,10,15,0.92), rgba(18,18,26,0.88)), url('https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1600&q=80'); background-size: cover; background-position: center;">
```

- [ ] **Step 3: Update hero title to use glitch effect**

Find the main title (the `display-title` element). Wrap or replace with glitch-text version:

Find:
```html
<h1 class="display-title">
```

Add `glitch-text` class and `data-text` attribute to the inner text span that uses `text-gradient`:

The title with `text-gradient` class — add `neon-text` alongside or replace `text-gradient` with `cyber-gradient`:

Find `text-gradient` in the title area and replace with `cyber-gradient neon-text`.

- [ ] **Step 4: Update stat cards in hero**

Find each `.stat-card` in the hero section. Add `.cyber-corner` class to each:

Find:
```html
<div class="stat-card
```

Replace each occurrence with:
```html
<div class="stat-card cyber-corner
```

- [ ] **Step 5: Update game showcase cards**

In the game scenes section (the horizontal scrolling rail), each game card should include:
- A background image from `GAME_IMAGES`
- Updated card styling with neon effects

Find game card elements in the snap-scroll rail. For each game card, add a background image div and update the styling. Add `scanline-overlay` to each card wrapper.

- [ ] **Step 6: Update service promises section**

Find the 3 promise cards (lg:grid-cols-3 section). Add `cyber-corner` class to each:

Replace each promise card's class list to include `card-hover cyber-corner`.

- [ ] **Step 7: Update journey steps section**

The 4-step flow should have gradient connector lines. The step number circles should get neon borders:

Find step circle styles and add:
```
border-color: rgba(0, 240, 255, 0.5);
box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
```

- [ ] **Step 8: Update CTA section**

The bottom CTA section — add `scanline-overlay` class and update button to `clip-angle-lg`.

- [ ] **Step 9: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/HomeView.vue
git commit -m "feat(frontend): cyberpunk redesign for HomeView"
```

---

## Task 7: LoginView — Cyberpunk Form Styling

**Files:**
- Modify: `frontend/src/views/LoginView.vue` (178 lines)

- [ ] **Step 1: Add background image import**

In `<script setup>`, add:

```js
import { PAGE_BACKGROUNDS } from '@/data/gameImages.js'
```

- [ ] **Step 2: Add page background**

Wrap the root `<div class="page-shell">` content with a background layer. Find:

```html
<div class="page-shell">
```

Replace with:

```html
<div class="page-shell relative">
  <div class="pointer-events-none absolute inset-0 -z-10 overflow-hidden rounded-[28px]" style="background-image: linear-gradient(135deg, rgba(10,10,15,0.95), rgba(18,18,26,0.9)); "></div>
```

(And close the extra div at the end)

- [ ] **Step 3: Update hero-panel (left section)**

Find:
```html
<section class="hero-panel flex flex-col justify-between p-6 sm:p-8 lg:p-10">
```

Replace with:
```html
<section class="hero-panel scanline-overlay flex flex-col justify-between p-6 sm:p-8 lg:p-10">
```

Update the section title to use `.glitch-text`:

Find the main heading in the left section. Add `glitch-text` class and `data-text` attribute matching the text content.

- [ ] **Step 4: Update form card (right section)**

The form card (`.surface-card`) already gets the cyberpunk styling from Task 2. Add `.cyber-corner`:

Find:
```html
<section class="surface-card p-6 sm:p-8 lg:p-10">
```

Replace with:
```html
<section class="surface-card cyber-corner p-6 sm:p-8 lg:p-10">
```

- [ ] **Step 5: Update login button**

Find the login submit button. Add `clip-angle-sm` class:

If it has `btn-primary`, it already gets the new clip-path from Task 2. No additional change needed.

- [ ] **Step 6: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/LoginView.vue
git commit -m "feat(frontend): cyberpunk styling for LoginView"
```

---

## Task 8: RegisterView — Mirror of Login Styling

**Files:**
- Modify: `frontend/src/views/RegisterView.vue` (221 lines)

- [ ] **Step 1: Apply same pattern as LoginView**

Same changes as Task 7 but mirrored (form left, hero right):

- Add `PAGE_BACKGROUNDS` import
- Add `scanline-overlay` to `.hero-panel`
- Add `cyber-corner` to `.surface-card` form section
- Add glitch-text class to the main heading in the hero section

- [ ] **Step 2: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/RegisterView.vue
git commit -m "feat(frontend): cyberpunk styling for RegisterView"
```

---

## Task 9: OrderList — Order Cards + Filters Redesign

**Files:**
- Modify: `frontend/src/views/OrderList.vue` (397 lines)

- [ ] **Step 1: Add game images import**

In `<script setup>`, add:

```js
import { getGameImage } from '@/data/gameImages.js'
```

- [ ] **Step 2: Update page header**

Find the page title. Add `neon-text` class.

Find stat cards in the hero section. Add `cyber-corner` class to each. Update number elements to include `neon-text-amber`.

- [ ] **Step 3: Update filter section**

The quick game buttons should show as capsule tags. Find the game button area and update each button:

Find game name buttons (the hot game quick-select buttons). Update selected state to use cyan glow:

For the selected state, change the active class to include `shadow-glow-neon` and `border-cyan-400/50`.

- [ ] **Step 4: Update order cards with status lines**

For each order card in the grid, add a left status-colored border. The card template iterates over orders — find the card wrapper element.

In the v-for loop rendering order cards, dynamically add the status line class:

```html
<div :class="['card-hover', 'status-line-' + order.status.toLowerCase()]"
```

This adds a 2px left border colored by order status using the utility classes from Task 2.

- [ ] **Step 5: Update price display**

Find the price display element in order cards. Add `neon-text-amber` class to the price number.

- [ ] **Step 6: Update pagination**

Find the current page button. Add cyan glow styling:

For the active page number button, update its classes to include:
```
bg-cyan-500/20 text-cyan-300 shadow-glow-neon
```

- [ ] **Step 7: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/OrderList.vue
git commit -m "feat(frontend): cyberpunk styling for OrderList"
```

---

## Task 10: OrderCreate — AI Step + Form Redesign

**Files:**
- Modify: `frontend/src/views/OrderCreate.vue` (411 lines)

- [ ] **Step 1: Update hero panel**

Add `scanline-overlay` to the hero section.

- [ ] **Step 2: Update AI analyze button**

Find the "AI 分析" button. Add `animate-neon-pulse` class for the pulsing glow effect.

- [ ] **Step 3: Update Step 1 textarea**

The textarea for AI input — add a very faint scanline background:

```html
style="background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,240,255,0.01) 3px, rgba(0,240,255,0.01) 4px), rgba(18,18,26,0.8);"
```

- [ ] **Step 4: Update game buttons with images**

Add `getGameImage` import and update hot game buttons.

- [ ] **Step 5: Update preview card**

Find the sidebar preview card. Add `cyber-corner` class.

- [ ] **Step 6: Update risk warning**

Find the AI risk warning display. Update its classes to use neon-pink border with glitch:

```html
<div class="rounded-2xl p-4 animate-glitch-once" style="border: 1px solid rgba(255,45,107,0.5); background: rgba(255,45,107,0.1);">
```

- [ ] **Step 7: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/OrderCreate.vue
git commit -m "feat(frontend): cyberpunk styling for OrderCreate"
```

---

## Task 11: OrderDetail — Timeline + Hero Redesign

**Files:**
- Modify: `frontend/src/views/OrderDetail.vue` (328 lines)

- [ ] **Step 1: Update hero section**

Add `scanline-overlay` to the hero-panel section.

- [ ] **Step 2: Update rank transition display**

Find the "current_rank → target_rank" display. Replace the arrow with a gradient styled element:

```html
<span class="mx-2 inline-block h-0.5 w-8" style="background: linear-gradient(90deg, #00f0ff, #fbbf24);"></span>
```

- [ ] **Step 3: Update stat cards**

Add `cyber-corner` class to each stat card in the hero.

- [ ] **Step 4: Update timeline**

Find the timeline section (numbered steps showing order lifecycle). Update the connector line between steps:

For each timeline node circle, update border to cyan neon:
```
border-color: rgba(0, 240, 255, 0.5);
box-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
```

For completed nodes, make them brighter. For pending nodes, use dark grey.

The connector line between nodes should use the gradient:
```
background: linear-gradient(180deg, #00f0ff, #b829dd);
```

- [ ] **Step 5: Update action buttons**

All action buttons already get the clip-path styling from Task 2 `.btn-primary` changes.

- [ ] **Step 6: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/OrderDetail.vue
git commit -m "feat(frontend): cyberpunk styling for OrderDetail"
```

---

## Task 12: ProfileView — Profile + Booster Application

**Files:**
- Modify: `frontend/src/views/ProfileView.vue` (380 lines)

- [ ] **Step 1: Update avatar**

Find the avatar circle element. Add a cyan neon halo:

Update the avatar div styles to include:
```
box-shadow: 0 0 20px rgba(0, 240, 255, 0.4), 0 0 40px rgba(0, 240, 255, 0.2);
border: 2px solid rgba(0, 240, 255, 0.5);
```

- [ ] **Step 2: Update form sections**

Find each `.surface-card` form block. Add `cyber-corner` class.

Find dividers between sections. Replace `border-b` or `<hr>` with:
```html
<div class="cyber-divider my-6"></div>
```

- [ ] **Step 3: Update stat cards**

Add `cyber-corner` to stat cards in the hero section.

- [ ] **Step 4: Update booster application area**

Find the upload area (for proof images). Update border to neon dashed:

```html
style="border: 1px dashed rgba(0, 240, 255, 0.4);"
```

- [ ] **Step 5: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/ProfileView.vue
git commit -m "feat(frontend): cyberpunk styling for ProfileView"
```

---

## Task 13: AdminView — Dashboard Redesign

**Files:**
- Modify: `frontend/src/views/AdminView.vue` (398 lines)

- [ ] **Step 1: Update dashboard stats**

Find the 3 stat cards in the hero section. Add `cyber-corner` class to each. Color-code the number glow:
- Applications count: `neon-text` (cyan)
- Pending orders: `neon-text-amber` (amber)
- Disputed orders: `neon-text-pink` (pink)

- [ ] **Step 2: Update application review cards**

For each application card, add a left status line using the application status:

Add dynamic class based on application status:
```html
:class="{ 'status-line-pending': app.status === 'PENDING', 'status-line-completed': app.status === 'APPROVED', 'status-line-disputed': app.status === 'REJECTED' }"
```

- [ ] **Step 3: Update order management cards**

Same as OrderList — add status line classes to each order card.

For intervention action buttons, use `btn-danger` (which now has neon-pink from Task 2).

- [ ] **Step 4: Update review form buttons**

Review approve/reject buttons — they already use `btn-success`/`btn-danger` which have cyberpunk styles from Task 2.

- [ ] **Step 5: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/AdminView.vue
git commit -m "feat(frontend): cyberpunk styling for AdminView"
```

---

## Task 14: NotFound — 404 Page Redesign

**Files:**
- Modify: `frontend/src/views/NotFound.vue` (25 lines)

- [ ] **Step 1: Rewrite NotFound.vue**

Replace entire template with cyberpunk 404 page:

```vue
<template>
  <div class="page-shell">
    <section class="hero-panel scanline-overlay p-8 sm:p-10 lg:p-14" style="background-image: linear-gradient(135deg, rgba(10,10,15,0.93), rgba(18,18,26,0.9)), url('https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1600&q=80'); background-size: cover; background-position: center;">
      <div class="mx-auto max-w-xl text-center space-y-6">
        <div class="glitch-text text-8xl sm:text-9xl font-black animate-glitch" data-text="404" style="color: #00f0ff;">404</div>
        <h2 class="section-title neon-text">页面未找到</h2>
        <p class="section-copy text-slate-400">你访问的页面不存在或已被移除</p>
        <div class="flex flex-wrap items-center justify-center gap-4 pt-4">
          <router-link to="/" class="btn-primary clip-angle-sm">返回首页</router-link>
          <router-link to="/orders" class="btn-secondary">订单大厅</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
</script>
```

- [ ] **Step 2: Commit**

```bash
cd e:/game-boosting-platform
git add frontend/src/views/NotFound.vue
git commit -m "feat(frontend): cyberpunk 404 page"
```

---

## Task 15: Docker Build Verification

- [ ] **Step 1: Build frontend in Docker**

```bash
cd e:/game-boosting-platform
docker-compose --env-file .env.local up -d --build frontend
```

- [ ] **Step 2: Check build succeeds**

```bash
docker-compose --env-file .env.local ps
```

Expected: `game-boosting-frontend` shows `Up ... (healthy)`

- [ ] **Step 3: Check all services running**

```bash
docker-compose --env-file .env.local ps
```

Expected: All 3 services (db, backend, frontend) are Up and healthy.

- [ ] **Step 4: Verify pages load**

Open browser and check:
- http://localhost:80 — homepage loads with cyberpunk styling
- http://localhost:80/login — login page with neon effects
- http://localhost:80/register — register page
- http://localhost:80/orders — order list (if logged in)
- http://localhost:80/nonexistent — 404 page with glitch effect

- [ ] **Step 5: Final commit if any fixes needed**

```bash
cd e:/game-boosting-platform
git add -A
git commit -m "fix(frontend): post-build adjustments for cyberpunk redesign"
```
