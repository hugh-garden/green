import { ScatterplotLayer } from '@deck.gl/layers'
import type { Layer } from '@deck.gl/core'
import { themeColor } from './cssColor'

// dropped pin location — position on globe
export interface GeoPin {
  longitude: number
  latitude: number
}

// meters above the surface — avoids z-fighting
const PIN_ALTITUDE = 100000

// build the dropped-pin layer - sticks to globe surface
export function createPinLayer(pin: GeoPin | null): Layer {
  return new ScatterplotLayer<GeoPin>({
    id: 'pin',
    data: pin ? [pin] : [],
    getPosition: (pin) => [pin.longitude, pin.latitude, PIN_ALTITUDE],
    getFillColor: themeColor('--color-pin'),
    getRadius: 40000,
    radiusMinPixels: 4,
    radiusMaxPixels: 10,
  })
}
