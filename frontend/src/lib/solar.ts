import type { ClimateData } from './climate'

export type SolarBand = 'excellent' | 'very good' | 'viable' | 'marginal' | 'poor'

export type SolarPotential =
  | { band: 'no data'; optimalTilt: number }
  | { band: SolarBand; ghiAnnual: number; optimalTilt: number }

// global solar atlas doesn't cover latitudes outside this range at all
const COVERAGE_LAT_MIN = -60
const COVERAGE_LAT_MAX = 65

// viability bands for annual GHI in kWh/m²/yr, roughly following global solar siting guidance
const BANDS: [number, SolarBand][] = [
  [2000, 'excellent'],
  [1600, 'very good'],
  [1300, 'viable'],
  [900, 'marginal'],
]

function bandFor(ghiAnnual: number): SolarBand {
  for (const [threshold, band] of BANDS) {
    if (ghiAnnual >= threshold) return band
  }
  return 'poor'
}

// rough solar pv viability for a pin — ghi_annual is a daily average (kWh/m²/day), so scale to /yr
export function scoreSolarPotential(climate: ClimateData, latitude: number): SolarPotential | null {
  // ideal fixed-panel tilt roughly tracks latitude — always computable, even without ghi coverage
  const optimalTilt = Math.round(Math.abs(latitude))

  if (latitude < COVERAGE_LAT_MIN || latitude > COVERAGE_LAT_MAX) {
    return { band: 'no data', optimalTilt }
  }
  if (climate.ghi_annual == null) return null

  const ghiAnnual = climate.ghi_annual * 365
  return { band: bandFor(ghiAnnual), ghiAnnual, optimalTilt }
}
