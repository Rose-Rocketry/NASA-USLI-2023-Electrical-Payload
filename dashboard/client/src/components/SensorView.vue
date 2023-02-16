<script setup lang="ts">
import SensorPlot from './SensorPlot.vue';
import type { ChannelType, SensorData } from '@/sensorData';
import { onUpdated } from 'vue';

const { data } = defineProps<{
  data: SensorData
}>()

// Packet used for guessing metadata
// We should use explicit metadata in the future (for units, etc...)

const referencePacket = data.packets.value[0];
const metaRaw = new Map<string, ChannelType>();
const metaPlot = new Map<string, ChannelType>();

for (let key in referencePacket) {
  if (key == "timestamp")
    continue;

  if (Array.isArray(referencePacket[key])) {
    metaPlot.set(key, "vector");
  } else if (typeof (referencePacket[key]) == "number") {
    metaPlot.set(key, "number");
  } else if (typeof (referencePacket[key]) == "boolean") {
    metaRaw.set(key, "boolean");
  } else if (typeof (referencePacket[key]) == "string") {
    metaRaw.set(key, "string");
  } else {
    metaRaw.set(key, "unknown");
  }
}
</script>

<template>
  <h2>
    <code>{{ data.id }}</code>:
    <code>{{ data.packets.value.length }}</code> datapoints
  </h2>
  <template v-for="[key, type] in metaRaw.entries()" :key="key">
    <template v-if="type == 'unknown'">
      <p>{{ key }}: Unknown type</p>
    </template>
    <template v-if="type == 'boolean' || type == 'string'">
      <!-- Just display latest value for bool's and strings -->
      <p>{{ key }}: <code>{{ JSON.stringify(data.packets.value[data.packets.value.length - 1][key]) }}</code></p>
    </template>
  </template>
  <div class="plots" v-if="metaPlot.size > 0">
    <template v-for="[key, type] in metaPlot.entries()" :key="key">
      <SensorPlot :channel-key="key" :channel-type="type" :packets="data.packets"></SensorPlot>
    </template>
</div>
</template>

<style scoped>
.plots {
  display: flex;
  flex-direction: column;
  margin: 10px 0;
}

@media (min-width: 1024px) {
  .plots {
    flex-direction: row;
  }
}
</style>
