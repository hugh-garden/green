import { API_BASE } from '../config'
import type { GeoPin } from './pins'

// known climate values for a coordinate — null where the raster has no data (e.g. open ocean)
export interface ClimateData {
  annual_mean_temp: number | null
  annual_precip: number | null
  elevation: number | null
  ghi_annual: number | null
}

// fetch known climate data for a pinned coordinate
export async function fetchClimate(pin: GeoPin): Promise<ClimateData> {
  const response = await fetch(`${API_BASE}/api/climate?lon=${pin.longitude}&lat=${pin.latitude}`)
  return response.json()
}
