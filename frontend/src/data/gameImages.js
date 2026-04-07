/**
 * Centralized game image data.
 * Each game with local assets has an array of hero images; one is picked at
 * random per session so the page feels fresh on every visit.
 */

/* ── local cover imports (Vite resolves these at build time) ── */
import genshin1 from '@/assets/images/games/genshin/1.jpg'
import genshin2 from '@/assets/images/games/genshin/2.jpg'
import genshin3 from '@/assets/images/games/genshin/3.jpg'
import genshin4 from '@/assets/images/games/genshin/4.jpg'
import genshin5 from '@/assets/images/games/genshin/5.png'

import valorant1 from '@/assets/images/games/valorant/1.jpg'
import valorant2 from '@/assets/images/games/valorant/2.jpg'
import valorant3 from '@/assets/images/games/valorant/3.jpg'
import valorant4 from '@/assets/images/games/valorant/4.jpg'
import valorant5 from '@/assets/images/games/valorant/5.jpg'

import honorOfKings1 from '@/assets/images/games/honor-of-kings/1.jpg'
import honorOfKings2 from '@/assets/images/games/honor-of-kings/2.jpg'
import honorOfKings3 from '@/assets/images/games/honor-of-kings/3.jpg'
import honorOfKings4 from '@/assets/images/games/honor-of-kings/4.jpg'
import honorOfKings5 from '@/assets/images/games/honor-of-kings/5.jpg'

import deltaForce1 from '@/assets/images/games/delta-force/1.jpg'
import deltaForce2 from '@/assets/images/games/delta-force/2.jpg'
import deltaForce3 from '@/assets/images/games/delta-force/3.jpg'
import deltaForce4 from '@/assets/images/games/delta-force/4.jpg'
import deltaForce5 from '@/assets/images/games/delta-force/5.jpg'

import tft1 from '@/assets/images/games/tft/1.jpg'
import tft2 from '@/assets/images/games/tft/2.jpg'
import tft3 from '@/assets/images/games/tft/3.jpg'
import tft4 from '@/assets/images/games/tft/4.jpg'
import tft5 from '@/assets/images/games/tft/5.jpg'

/* ── helpers ── */

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

/**
 * Session-stable random picks: we draw once at module-load so repeated calls
 * within the same page session return the same image.
 */
const sessionPicks = new Map()

function sessionRandom(key, arr) {
  if (!sessionPicks.has(key)) {
    sessionPicks.set(key, pickRandom(arr))
  }
  return sessionPicks.get(key)
}

/* ── per-game hero pool ── */

const GAME_HERO_POOLS = {
  '原神': [genshin1, genshin2, genshin3, genshin4, genshin5],
  '无畏契约': [valorant1, valorant2, valorant3, valorant4, valorant5],
  '王者荣耀': [honorOfKings1, honorOfKings2, honorOfKings3, honorOfKings4, honorOfKings5],
  '三角洲行动': [deltaForce1, deltaForce2, deltaForce3, deltaForce4, deltaForce5],
  '金铲铲之战': [tft1, tft2, tft3, tft4, tft5],
}

export const GAME_IMAGES = {
  '王者荣耀': {
    heroPool: GAME_HERO_POOLS['王者荣耀'],
    get hero() { return sessionRandom('王者荣耀', this.heroPool) },
    color: '#ff6b2b',
    gradient: 'from-orange-500/20 to-red-600/20',
  },
  '原神': {
    heroPool: GAME_HERO_POOLS['原神'],
    get hero() { return sessionRandom('原神', this.heroPool) },
    color: '#a78bfa',
    gradient: 'from-violet-500/20 to-purple-600/20',
  },
  '无畏契约': {
    heroPool: GAME_HERO_POOLS['无畏契约'],
    get hero() { return sessionRandom('无畏契约', this.heroPool) },
    color: '#ff4655',
    gradient: 'from-red-500/20 to-rose-600/20',
  },
  '三角洲行动': {
    heroPool: GAME_HERO_POOLS['三角洲行动'],
    get hero() { return sessionRandom('三角洲行动', this.heroPool) },
    color: '#f5c518',
    gradient: 'from-yellow-500/20 to-amber-600/20',
  },
  '金铲铲之战': {
    heroPool: GAME_HERO_POOLS['金铲铲之战'],
    get hero() { return sessionRandom('金铲铲之战', this.heroPool) },
    color: '#00a3ff',
    gradient: 'from-blue-500/20 to-cyan-600/20',
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
 * Get all hero images for a game (for galleries / preloading).
 */
export function getGameHeroPool(gameName) {
  return GAME_HERO_POOLS[gameName] || []
}

/**
 * Force a fresh random pick for a game (e.g. on manual refresh).
 */
export function refreshGameHero(gameName) {
  const pool = GAME_HERO_POOLS[gameName]
  if (pool) {
    sessionPicks.set(gameName, pickRandom(pool))
  }
  return sessionPicks.get(gameName) || null
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
