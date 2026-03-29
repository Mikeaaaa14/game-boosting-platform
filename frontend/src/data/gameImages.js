/**
 * Centralized game image data.
 * Hero images are external URLs (lazy loaded with fallback).
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
