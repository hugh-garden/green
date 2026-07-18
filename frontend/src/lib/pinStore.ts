import { computed, ref } from 'vue'
import type { GeoPin } from './pins'

// every pin dropped on the globe
export const pins = ref<GeoPin[]>([])
// id of the pin currently shown in the side panel, if any
export const selectedPinId = ref<string | null>(null)

// the pin currently shown in the side panel, if any
export const selectedPin = computed(
  () => pins.value.find((pin) => pin.id === selectedPinId.value) ?? null,
)

// add a pin at a coordinate, select it, and return it
export function addPin(
  longitude: number,
  latitude: number,
  country: string | null,
  state: string | null,
  subunit: string | null,
): GeoPin {
  const pin: GeoPin = { id: crypto.randomUUID(), longitude, latitude, country, state, subunit }
  pins.value = [...pins.value, pin]
  selectedPinId.value = pin.id
  return pin
}

// show a pin's data in the side panel
export function selectPin(id: string): void {
  selectedPinId.value = id
}

// remove a pin, deselecting it first if it was selected
export function removePin(id: string): void {
  pins.value = pins.value.filter((pin) => pin.id !== id)
  if (selectedPinId.value === id) selectedPinId.value = null
}
