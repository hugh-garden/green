// deck.gl's GlobeView renders at (zoom - zoomAdjust(latitude)) to mimic web mercator distortion near the poles — mirror it here so we can hold visual scale constant across latitudes
export function zoomAdjust(latitude: number): number {
  return Math.log2(Math.PI * Math.cos((latitude * Math.PI) / 180))
}
