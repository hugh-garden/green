import { GeoJsonLayer } from '@deck.gl/layers'
import type { Layer } from '@deck.gl/core'
import { fetchGeoLayer } from './api'
import { themeColor } from './cssColor'

// build the ocean, country, region, and coastline layers for the globe view
export async function createGeoLayers(): Promise<Layer[]> {
  const [ocean, countries, states, subunits, coastline] = await Promise.all([
    fetchGeoLayer('ocean'),
    fetchGeoLayer('countries'),
    fetchGeoLayer('states'),
    fetchGeoLayer('subunits'),
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
      // lets hover distinguish "over the globe" from "over empty space" for cursor/drag gating
      pickable: true,
    }),
    // land fill only — split from the border so the border can be drawn above region lines, below
    new GeoJsonLayer({
      id: 'countries-fill',
      data: countries,
      filled: true,
      stroked: false,
      getFillColor: themeColor('--color-land-fill'),
      // lets clicks be tested against land — used to keep pins off the ocean
      pickable: true,
    }),
    // state/province boundaries — filled invisibly so the whole area is pickable, not just the line
    new GeoJsonLayer({
      id: 'states',
      data: states,
      filled: true,
      stroked: true,
      getFillColor: [0, 0, 0, 0],
      getLineColor: themeColor('--color-region-line'),
      lineWidthMinPixels: 0.5,
      pickable: true,
    }),
    // geographic subunits (e.g. uk home nations) — same picking trick as states
    new GeoJsonLayer({
      id: 'subunits',
      data: subunits,
      filled: true,
      stroked: true,
      getFillColor: [0, 0, 0, 0],
      getLineColor: themeColor('--color-region-line'),
      lineWidthMinPixels: 0.5,
      pickable: true,
    }),
    // country border only — drawn after region lines so it wins where the two coincide
    new GeoJsonLayer({
      id: 'countries-line',
      data: countries,
      filled: false,
      stroked: true,
      getLineColor: themeColor('--color-land-stroke'),
      lineWidthMinPixels: 0.7,
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
