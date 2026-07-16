# conventions

## comments

- only single-line comments: `//` in ts/js, `#` in python
- never block comments or docstrings (`/* */`, `"""..."""`), never a comment spanning multiple lines
- css has no `//`/`#` syntax — single-line `/* ... */` only, one line, never a multi-line block
- as brief as possible
- first word lowercase

## css

- no inline styles, ever (no `style=""` attributes, no JS-computed inline styles)
- colors are hex codes only (`#rrggbb`) — no `rgb()`, `rgba()`, `hsl()`, named colors
- shared/theme values (colors, spacing, etc.) live as CSS custom properties in
  `frontend/src/styles/theme.css` — the single source of truth
- global resets and cross-cutting rules live in `frontend/src/styles/base.css`
- component-specific layout stays in that component's own SFC `<style scoped>`
  block — never redefine a shared token there, reference the CSS var instead
- code that needs a color in JS (e.g. deck.gl layer accessors, which can't be
  styled with CSS since they render to a WebGL canvas, not the DOM) reads the
  CSS custom property at runtime via `frontend/src/lib/cssColor.ts` rather
  than hardcoding a duplicate value

## ts / vue

- small, single-responsibility modules — avoid big scripts that mix concerns
- `src/lib/` — framework-agnostic logic (API calls, data transforms, utils)
- `src/components/` — vue SFCs; a component orchestrates, it doesn't contain
  business logic inline
- `src/styles/` — global CSS (theme tokens, resets)
