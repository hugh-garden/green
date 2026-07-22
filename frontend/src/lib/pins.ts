import { ScatterplotLayer } from '@deck.gl/layers'
import type { Layer } from '@deck.gl/core'
import { themeColor } from './cssColor'

// dropped pin location and identity
export interface GeoPin {
  id: string
  longitude: number
  latitude: number
  country: string | null
  state: string | null
  subunit: string | null
}

// meters above the surface — avoids z-fighting
const PIN_ALTITUDE = 100000
// fixed screen size regardless of zoom, so the click/right-click radius stays predictable
const PIN_RADIUS_PIXELS = 8

// build the pins layer — sticks to globe surface, constant on-screen radius
export function createPinsLayer(pins: GeoPin[], selectedPinId: string | null): Layer {
  const fillColor = themeColor('--color-pin')
  const selectedFillColor = themeColor('--color-pin-selected')

  return new ScatterplotLayer<GeoPin>({
    id: 'pins',
    data: pins,
    pickable: true,
    radiusUnits: 'pixels',
    getPosition: (pin) => [pin.longitude, pin.latitude, PIN_ALTITUDE],
    getFillColor: (pin) => (pin.id === selectedPinId ? selectedFillColor : fillColor),
    updateTriggers: { getFillColor: selectedPinId },
    getRadius: PIN_RADIUS_PIXELS,
  })
}
