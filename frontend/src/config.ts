// backend origin — override via VITE_API_BASE for non-local environments
export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
