import { API_BASE } from '../config'

// fetch a named GeoJSON layer from the backend
export async function fetchGeoLayer(name: string): Promise<unknown> {
  const response = await fetch(`${API_BASE}/api/geo/${name}`)
  return response.json()
}
