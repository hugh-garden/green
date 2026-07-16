// offscreen 1x1 canvas — lets the browser parse any valid CSS color syntax for us
const canvas = document.createElement('canvas')
canvas.width = 1
canvas.height = 1
const ctx = canvas.getContext('2d', { willReadFrequently: true })!

// convert a CSS color string to a deck.gl rgba array
export function cssColorToRgba(color: string): [number, number, number, number] {
  ctx.clearRect(0, 0, 1, 1)
  ctx.fillStyle = color
  ctx.fillRect(0, 0, 1, 1)
  const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data
  return [r, g, b, a]
}

// read a CSS custom property off :root and convert it to a deck.gl rgba array
export function themeColor(cssVariable: string): [number, number, number, number] {
  const value = getComputedStyle(document.documentElement).getPropertyValue(cssVariable)
  return cssColorToRgba(value.trim())
}
