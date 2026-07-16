<script setup lang="ts">
import { onMounted, onBeforeUnmount, useTemplateRef } from 'vue'
import { Deck, _GlobeView as GlobeView, type Layer } from '@deck.gl/core'
import { createGeoLayers } from '../lib/geoLayers'
import { createPinLayer, type GeoPin } from '../lib/pins'

const container = useTemplateRef<HTMLDivElement>('container')
let deck: Deck<GlobeView> | null = null
let baseLayers: Layer[] = []
// deck.gl diffs layer props by reference, so this must be replaced, never mutated in place
let pin: GeoPin | null = null

// re-render with the current base layers plus a fresh pin layer
function renderLayers() {
  deck?.setProps({ layers: [...baseLayers, createPinLayer(pin)] })
}

// mount the deck.gl globe once the container element exists
onMounted(async () => {
  baseLayers = await createGeoLayers()

  deck = new Deck({
    parent: container.value ?? undefined,
    views: new GlobeView(),
    initialViewState: { longitude: 0, latitude: 20, zoom: 0 },
    // eases to a stop after a drag rather than snapping still
    controller: { inertia: 300, doubleClickZoom: false },
    // a double click drops a pin at the clicked geo coordinate
    onClick: (info, event) => {
      if (event.tapCount === 2 && info.coordinate) {
        pin = { longitude: info.coordinate[0], latitude: info.coordinate[1] }
        renderLayers()
      }
    },
    layers: [],
  })

  renderLayers()
})

// release WebGL resources when the component unmounts
onBeforeUnmount(() => {
  deck?.finalize()
})
</script>

<template>
  <div ref="container" class="globe-container" />
</template>

<style scoped>
/* fill the viewport — deck.gl attaches its canvas to this element */
.globe-container {
  position: fixed;
  inset: 0;
}
</style>
