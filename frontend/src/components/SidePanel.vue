<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { selectedPin } from '../lib/pinStore'
import { fetchClimate, type ClimateData } from '../lib/climate'
import { scoreSolarPotential } from '../lib/solar'

const climate = ref<ClimateData | null>(null)

// refetch known climate data whenever the pin changes
watch(selectedPin, async (pin) => {
  climate.value = pin ? await fetchClimate(pin) : null
})

// derived from climate + latitude, no fetch needed
const solar = computed(() => {
  const pin = selectedPin.value
  return climate.value && pin ? scoreSolarPotential(climate.value, pin.latitude) : null
})

// state, subunit, and country together — drops any that are missing or redundant with the country
const locationLabel = computed(() => {
  const pin = selectedPin.value
  if (!pin) return ''
  const country = pin.country ?? 'unknown'
  const parts = [pin.state, pin.subunit].filter(
    (part): part is string => !!part && part !== country,
  )
  parts.push(country)
  return parts.join(', ')
})
</script>

<template>
  <aside class="side-panel">
    <h1 class="side-panel__title">green</h1>
    <div class="panel-hint">
      <p>double click on the map to drop a pin</p>
      <p>click on a pin to see details</p>
      <p>right click to remove</p>
    </div>
    <div v-if="selectedPin" class="panel-climate">
      <p>{{ selectedPin.latitude.toFixed(2) }}, {{ selectedPin.longitude.toFixed(2) }}</p>
      <p>{{ locationLabel }}</p>
      <p>annual mean temperature: {{ climate?.annual_mean_temp?.toFixed(1) ?? '—' }}°c</p>
      <p>annual precipitation: {{ climate?.annual_precip?.toFixed(0) ?? '—' }}mm</p>
      <p>elevation: {{ climate?.elevation?.toFixed(0) ?? '—' }}m</p>
      <p>solar potential: {{ solar?.band ?? '—' }}<template v-if="solar && solar.band !== 'no data'"> ({{ solar.ghiAnnual.toFixed(0) }} kWh/m²/yr, {{ solar.optimalTilt }}° tilt)</template></p>
    </div>
  </aside>
</template>
