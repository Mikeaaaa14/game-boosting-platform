# Game Boosting Platform - Cyberpunk Redesign Spec

## Overview

Full-site visual redesign with cyberpunk aesthetics, built on top of the existing dark + cyan/amber color scheme. Medium intensity — redesign component visual language (cards, buttons, nav, badges) while preserving all page structures and functionality.

**Implementation approach**: CSS variables + Tailwind extension (Plan A). Changes concentrated in `tailwind.config.js` and `main.css`, with per-page class replacements in `.vue` files. No new dependencies, no structural changes.

**Image strategy**: Hybrid — game logos and UI textures stored locally in `src/assets/images/`, large hero/background images loaded via external URLs with lazy loading and fallback.

**Page priority** (by user journey):
1. HomeView
2. LoginView + RegisterView
3. OrderList
4. OrderCreate
5. OrderDetail
6. ProfileView
7. AdminView
8. NotFound

---

## 1. Design System

### 1.1 Extended Color Palette

Additions to `tailwind.config.js` theme.extend.colors:

| Token | Values | Usage |
|---|---|---|
| `neon-pink` | `#ff2d6b` (base), `#ff6b9d` (light) | Cyberpunk accent, hover highlights, warnings |
| `neon-purple` | `#b829dd` (base), `#d946ef` (light) | Secondary accent, gradient pairing with cyan |
| `cyber-blue` | `#00f0ff` | Brighter neon version of cyan for glow effects |
| `dark-base` | `#0a0a0f` | Deeper black body background |
| `dark-surface` | `#12121a` | Card/panel backgrounds |
| `dark-elevated` | `#1a1a2e` | Modals, hover states, focus backgrounds |

Preserved unchanged:
- Primary cyan series (navigation, primary buttons, links)
- Accent amber series (prices, ratings, important numbers)
- Text colors white / slate-300 / slate-400 (hierarchy unchanged)

### 1.2 Visual Effect Tokens

New CSS custom properties and utility classes:

| Token | Definition | Usage |
|---|---|---|
| `neon-glow` | `box-shadow: 0 0 20px rgba(0,240,255,0.3)` | Card hover, active states |
| `cyber-gradient` | `linear-gradient(135deg, cyan-500, neon-purple, neon-pink)` | Title decorations, dividers |
| `scanline` | Repeating semi-transparent horizontal lines via pseudo-element | CRT scanline overlay on hero panels |
| `glitch` | Keyframe animation with `::before`/`::after` offset + color separation | Feature titles (sparingly) |
| `clip-angle-sm` | `clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px))` | Small buttons |
| `clip-angle-lg` | Same pattern with 16px cuts | CTA buttons, hero panels |

### 1.3 Animations

Added to `tailwind.config.js` theme.extend.animation/keyframes:

| Name | Effect | Duration |
|---|---|---|
| `glitch` | Text offset jitter with color channel separation | 2s, infinite, used sparingly |
| `scanline-move` | Vertical translate of scanline texture | 8s, linear, infinite |
| `neon-pulse` | Subtle box-shadow brightness oscillation | 2s, ease-in-out, infinite |
| `flow-line` | Gradient position shift along a line (for timeline connectors) | 3s, linear, infinite |

---

## 2. Component Redesign

### 2.1 Buttons

| Class | Changes |
|---|---|
| `.btn-primary` | Add `clip-angle-sm`; background: cyan-to-neon-purple gradient; hover: neon-glow + 1px translate-y |
| `.btn-secondary` | Border: 1px dashed neon-pink; hover: fill semi-transparent neon-pink |
| `.btn-ghost` | Transparent; hover: scanline texture sweeps across background |
| `.btn-danger` | Background: neon-pink; hover: glitch micro-jitter |
| `.btn-success` | Keep emerald; add neon-glow on hover |

### 2.2 Cards

| Class | Changes |
|---|---|
| `.surface-card` | Background: `dark-surface`; border: 1px `rgba(0,240,255,0.15)`; top-left: 2px neon decorative line at 45deg angle via `::before`; hover: border brightness increase + neon-glow |
| `.card-hover` | Hover: translate-y -2px + cyan neon shadow below |
| `.hero-panel` | Add scanline overlay via `::after` (pointer-events:none); border: gradient stroke |

### 2.3 Navigation

| Element | Changes |
|---|---|
| Sticky top nav | Background: `backdrop-blur-xl` frosted glass + bottom 1px gradient border (cyan -> transparent -> neon-pink); Logo text: one-shot glitch animation on load |
| `.nav-chip-active` | Background: semi-transparent cyan + neon-glow; text-shadow |
| `.nav-chip-idle` | Hover: scanline texture sweep |

### 2.4 Form Elements

| Element | Changes |
|---|---|
| `.input` | Focus: cyan border + neon-glow; background shifts to `dark-elevated` |
| `.input-error` | Border: neon-pink + neon-pink glow |
| Dropdowns | Same as `.input` styling; option hover: `dark-elevated` |

### 2.5 Status Badges

| Class | Changes |
|---|---|
| `.badge-pending` | Keep amber tone; add subtle `neon-pulse` animation |
| `.badge-locked` | Cyan border + scanline texture background |
| `.badge-completed` | Keep emerald; brief neon flash after render |
| `.badge-disputed` | neon-pink background + glitch micro-jitter |
| `.badge-cancelled` | Keep grey, no effects |

### 2.6 New Utility Classes

| Class | Effect |
|---|---|
| `.cyber-divider` | Gradient divider line: cyan -> transparent -> neon-pink (replaces `border-b`) |
| `.glitch-text` | Title glitch effect via `::before`/`::after` with offset + color separation |
| `.scanline-overlay` | Full-area scanline texture overlay (pointer-events: none) |
| `.neon-text` | Text + text-shadow glow |
| `.cyber-corner` | Four corner decorative L-shaped lines via pseudo-elements |
| `.clip-angle-sm` | 8px corner cuts |
| `.clip-angle-lg` | 16px corner cuts |

---

## 3. Image Resources

### 3.1 Local Assets (bundled)

Directory: `frontend/src/assets/images/`

| Path | Content | Size est. |
|---|---|---|
| `games/wzry-logo.png` | King of Glory logo | ~30KB |
| `games/lol-logo.png` | League of Legends logo | ~30KB |
| `games/pubg-logo.png` | PUBG Mobile logo | ~30KB |
| `games/genshin-logo.png` | Genshin Impact logo | ~30KB |
| `games/naraka-logo.png` | Naraka: Bladepoint logo | ~30KB |
| `ui/cyber-grid.svg` | Cyberpunk grid texture | ~5KB |
| `ui/scanline.svg` | Scanline texture | ~2KB |
| `ui/noise.png` | Noise grain texture | ~10KB |

Total local additions: ~170KB (`.cyber-corner` implemented via pure CSS pseudo-elements, no SVG needed)

### 3.2 External Assets (runtime loaded)

| Location | Content | Source |
|---|---|---|
| HomeView hero background | Cyberpunk city / multi-game composite | Unsplash cyberpunk images |
| HomeView game showcase | Per-game hero/scene wide images (5) | Game official promotional art URLs |
| LoginView / RegisterView background | Cyberpunk atmosphere | Unsplash |
| NotFound background | Glitch screen / cyber scene | Unsplash |

### 3.3 Image Error Handling

- All `<img>` tags: `loading="lazy"`
- `onerror` handler: fall back to CSS gradient background
- Loading state: `dark-surface` background + pulse skeleton animation

---

## 4. Per-Page Design

### 4.1 HomeView

| Section | Changes |
|---|---|
| Hero | Full-screen external cyberpunk background + scanline overlay + dark vignette gradient mask; main title: `.glitch-text`; subtitle: `.neon-text` cyan; CTA buttons: `.clip-angle-lg` + neon gradient |
| Stats bar | Numbers: amber `.neon-text`; cards: `.cyber-corner` decorations |
| Game carousel | Each card: external hero image top (with dark vignette), local game logo overlay top-left, info area `.surface-card` style; navigation arrows: neon style; dividers: `.cyber-divider` |
| Service promises | Icons: SVG neon line-art style; cards: hover neon-glow |
| 4-step flow | Connector lines: cyber-gradient + `flow-line` pulse animation; step circles: neon border |
| Footer | Top `.cyber-divider`; background: `cyber-grid.svg` texture overlay |

### 4.2 LoginView

| Section | Changes |
|---|---|
| Page background | External cyberpunk atmosphere image + dark overlay + scanline |
| Left description | Title: `.glitch-text`; feature list items: neon dot markers |
| Right form card | `.surface-card` + `.cyber-corner`; inputs: cyan focus glow; login button: `.clip-angle-sm` + gradient |

### 4.3 RegisterView

Mirror of LoginView layout (form left, description right). Same visual treatment.

### 4.4 OrderList

| Section | Changes |
|---|---|
| Page header | Title: `.neon-text`; stat cards: `.cyber-corner` + amber number glow |
| Filter bar | Game shortcut buttons: capsule tags with game logo icons (20px); selected state: cyan glow border |
| Order cards | Left 2px vertical gradient decoration line (color follows order status); game logo icon next to game name; price: amber `.neon-text`; hover: neon-glow + micro lift |
| Pagination | Current page: cyan fill + glow; arrow buttons: clip-angle |

### 4.5 OrderCreate

| Section | Changes |
|---|---|
| Step 1 AI analysis | Textarea: very faint scanline texture background; hot game buttons: with logo icons; "AI Analyze" button: `neon-pulse` animation |
| Step 2 form | Standard form styling; preview card: `.cyber-corner` |
| AI risk warning | neon-pink border + glitch micro-jitter animation |

### 4.6 OrderDetail

| Section | Changes |
|---|---|
| Hero section | Game name + status badge enlarged; rank "current -> target" connected by gradient arrow (cyan -> amber) |
| Timeline | Node connector: neon gradient line + `flow-line` pulse; completed nodes: bright, pending: dark grey; node circles: neon border |
| Action buttons | Unified clip-angle style |

### 4.7 ProfileView

| Section | Changes |
|---|---|
| Header | Avatar outer ring: cyan neon halo; role badge: color-matched glow |
| Edit sections | Each form block: `.surface-card` + `.cyber-corner`; blocks separated by `.cyber-divider` |
| Booster application | Status: large status badge display; upload area: dashed neon border |

### 4.8 AdminView

| Section | Changes |
|---|---|
| Stat cards | `.cyber-corner` + number glow; different neon colors per metric |
| Application review list | Card left side: status-colored vertical line; review form buttons: `.clip-angle-sm` |
| Order management list | Same as OrderList card style; action buttons: neon-pink (intervention = warning color) |

### 4.9 NotFound

Full-screen external glitch/cyber scene background + scanline; "404" number: oversized `.glitch-text` with continuous animation; return button: neon style.

---

## 5. Files Modified

### Config files
- `frontend/tailwind.config.js` — extend colors, animations, keyframes

### CSS
- `frontend/src/assets/main.css` — new/modified component classes, utility classes, keyframes

### Vue pages (class replacements only, no structural changes)
- `frontend/src/App.vue` — nav bar
- `frontend/src/views/HomeView.vue`
- `frontend/src/views/LoginView.vue`
- `frontend/src/views/RegisterView.vue`
- `frontend/src/views/OrderList.vue`
- `frontend/src/views/OrderCreate.vue`
- `frontend/src/views/OrderDetail.vue`
- `frontend/src/views/ProfileView.vue`
- `frontend/src/views/AdminView.vue`
- `frontend/src/views/NotFound.vue`

### New files
- `frontend/src/assets/images/games/*.png` — 5 game logos
- `frontend/src/assets/images/ui/*.svg` + `noise.png` — UI textures

### Not modified
- All backend files
- All stores, router, utils JS files (logic unchanged)
- docker-compose, Dockerfile, .env files
