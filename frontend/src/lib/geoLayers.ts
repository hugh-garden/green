import { GeoJsonLayer } from '@deck.gl/layers'
import type { Layer } from '@deck.gl/core'
import { fetchGeoLayer } from './api'
import { themeColor } from './cssColor'

// build the ocean, country, and coastline layers for the globe view
export async function createGeoLayers(): Promise<Layer[]> {
  const [ocean, countries, coastline] = await Promise.all([
    fetchGeoLayer('ocean'),
    fetchGeoLayer('countries'),
    fetchGeoLayer('coastline'),
  ])

  return [
    // drawn first so land and coastline render on top of it
    new GeoJsonLayer({
      id: 'ocean',
      data: ocean,
      filled: true,
      stroked: false,
      getFillColor: themeColor('--color-ocean'),
    }),
    new GeoJsonLayer({
      id: 'countries',
      data: countries,
      filled: true,
      stroked: true,
      getFillColor: themeColor('--color-land-fill'),
      getLineColor: themeColor('--color-land-stroke'),
      lineWidthMinPixels: 0.5,
    }),
    new GeoJsonLayer({
      id: 'coastline',
      data: coastline,
      filled: false,
      stroked: true,
      getLineColor: themeColor('--color-coastline'),
      lineWidthMinPixels: 1.5,
    }),
  ]
}
