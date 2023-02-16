<script setup lang="ts">
import type { ChannelType } from '@/sensorData';
import { onMounted, onUpdated, ref, watch, type Ref } from 'vue';
import Plotly from 'plotly.js-dist-min'

const plotEl = ref<HTMLElement>()

const props = defineProps<{
  channelKey: string,
  channelType: ChannelType,
  packets: Ref<any[]>,
}>()

const vectorNames = ['x', 'y', 'z', 'w']; // TODO: Get from metadata

function getTraces(): Plotly.Data[] {
  let xValues = props.packets.value.map(packet => new Date(packet['timestamp'] * 1000))
  let yValues = props.packets.value.map(packet => packet[props.channelKey])

  if (props.channelType == 'number') {
    return [{
      x: xValues,
      y: yValues,
      mode: 'lines'
    }]
  } else if (props.channelType == 'vector') {
    const names = vectorNames.slice(0, yValues[0].length)

    return names.map((name, i) => ({
      x: xValues,
      y: yValues.map(vector => vector[i]),
      mode: 'lines',
      name: name
    }))
  } else {
    return []
  }
}

function getLayout(): Partial<Plotly.Layout> {
  return {
    title: props.channelKey,
    margin: {
      l: 40,
      r: 40,
      t: 50,
      b: 40
    },
    xaxis: {
      tickangle: 0
    }
  }
}

onMounted(() => {
  Plotly.newPlot(plotEl.value!, getTraces(), getLayout(), { displayModeBar: false, responsive: true })
})

watch(props.packets, () => {
  Plotly.react(plotEl.value!, getTraces(), getLayout())
})
</script>

<template><div class="plot" ref="plotEl"></div></template>

<style scoped>
.plot {
  width: 800px;
  height: 300px;
}
</style>
