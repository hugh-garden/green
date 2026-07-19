<script setup lang="ts">
import { onMounted, onBeforeUnmount, useTemplateRef } from 'vue'
import { Deck, _GlobeView as GlobeView, LinearInterpolator, type Layer } from '@deck.gl/core'
import { createGeoLayers } from '../lib/geoLayers'
import { createPinsLayer, type GeoPin } from '../lib/pins'
import { zoomAdjust } from '../lib/globeZoom'
import { pins, selectedPinId, addPin, selectPin, removePin } from '../lib/pinStore'

const container = useTemplateRef<HTMLDivElement>('container')
let deck: Deck<GlobeView> | null = null
let baseLayers: Layer[] = []
// view state is held here and fed back to deck every change, so it can also be driven programmatically
interface GlobeViewState {
  longitude: number
  latitude: number
  zoom: number
  transitionDuration?: number
  transitionInterpolator?: LinearInterpolator
}
let viewState: GlobeViewState = { longitude: 0, latitude: 20, zoom: 0 }
// cursor and drag are gated on what's currently hovered — see onHover below
let cursorStyle = 'default'
let dragPanEnabled = true

// controller props, rebuilt whenever dragPan needs to flip
function controllerProps(dragPan: boolean) {
  return { inertia: 300, doubleClickZoom: false, dragPan }
}

// re-render with the current base layers plus the current pins
function renderLayers() {
  deck?.setProps({ layers: [...baseLayers, createPinsLayer(pins.value, selectedPinId.value)] })
}

// ease the view over to a pin's coordinates, correcting zoom so the visual scale stays constant
// (GlobeView renders at zoom - zoomAdjust(latitude), so holding zoom fixed would still look more/less zoomed in)
function flyToPin(pin: GeoPin) {
  const zoom = viewState.zoom - zoomAdjust(viewState.latitude) + zoomAdjust(pin.latitude)
  viewState = {
    ...viewState,
    longitude: pin.longitude,
    latitude: pin.latitude,
    zoom,
    transitionDuration: 500,
    transitionInterpolator: new LinearInterpolator(['longitude', 'latitude', 'zoom']),
  }
  deck?.setProps({ viewState })
}

// right click within a pin's radius removes it
async function handleContextMenu(event: MouseEvent) {
  event.preventDefault()
  const info = await deck?.pickObjectAsync({ x: event.offsetX, y: event.offsetY, layerIds: ['pins'] })
  if (info?.object) {
    removePin((info.object as GeoPin).id)
    renderLayers()
  }
}

// state/province name at a pixel, if the states layer has one there
async function pickState(x: number, y: number): Promise<string | null> {
  const pick = await deck?.pickObjectAsync({ x, y, layerIds: ['states'] })
  return (pick?.object as { properties?: { name?: string } } | undefined)?.properties?.name ?? null
}

// geographic subunit name at a pixel (e.g. uk home nations), if the subunits layer has one there
async function pickSubunit(x: number, y: number): Promise<string | null> {
  const pick = await deck?.pickObjectAsync({ x, y, layerIds: ['subunits'] })
  return (pick?.object as { properties?: { NAME?: string } } | undefined)?.properties?.NAME ?? null
}

// double click on land drops a new pin, tagged with its country/state/subunit, and centers the view on it
async function handleDoubleClick(longitude: number, latitude: number, x: number, y: number) {
  const countryPick = await deck?.pickObjectAsync({ x, y, layerIds: ['countries-fill'] })
  const country = (countryPick?.object as { properties?: { NAME?: string } } | undefined)?.properties?.NAME
  // no country hit means the click landed on the ocean — ignore it
  if (!country) return

  const [state, subunit] = await Promise.all([pickState(x, y), pickSubunit(x, y)])
  const pin = addPin(longitude, latitude, country, state, subunit)
  renderLayers()
  flyToPin(pin)
}

// mount the deck.gl globe once the container element exists
onMounted(async () => {
  baseLayers = await createGeoLayers()

  deck = new Deck({
    parent: container.value ?? undefined,
    views: new GlobeView(),
    viewState,
    // eases to a stop after a drag rather than snapping still
    controller: controllerProps(dragPanEnabled),
    // keeps our local copy in sync with drags/zooms so programmatic flights start from the right place
    onViewStateChange: ({ viewState: nextViewState }) => {
      viewState = nextViewState as typeof viewState
      deck?.setProps({ viewState })
    },
    // grabbing is only allowed over the globe itself — not over pins, not over empty space
    onHover: (info) => {
      const overGlobe = info.layer != null && info.layer.id !== 'pins'
      cursorStyle = overGlobe ? 'grab' : 'default'
      if (dragPanEnabled !== overGlobe) {
        dragPanEnabled = overGlobe
        deck?.setProps({ controller: controllerProps(dragPanEnabled) })
      }
    },
    getCursor: ({ isDragging }) => (isDragging ? 'grabbing' : cursorStyle),
    onClick: (info, event) => {
      // double click drops a new pin (handleDoubleClick checks it landed on actual land)
      if (event.tapCount === 2 && info.coordinate) {
        handleDoubleClick(info.coordinate[0], info.coordinate[1], info.x, info.y)
        return
      }
      // single click on a pin selects it — recolor immediately, then ease the view over
      if (event.tapCount === 1 && info.layer?.id === 'pins' && info.object) {
        const pin = info.object as GeoPin
        selectPin(pin.id)
        renderLayers()
        flyToPin(pin)
      }
    },
    layers: [],
  })

  container.value?.addEventListener('contextmenu', handleContextMenu)
  renderLayers()
})

// release WebGL resources and listeners when the component unmounts
onBeforeUnmount(() => {
  container.value?.removeEventListener('contextmenu', handleContextMenu)
  deck?.finalize()
})
</script>

<template>
  <div ref="container" class="globe-container" />
</template>
