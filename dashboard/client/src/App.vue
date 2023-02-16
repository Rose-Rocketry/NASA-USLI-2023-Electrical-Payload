<script setup lang="ts">
import StatusHeader from './components/StatusHeader.vue'
import SensorView from './components/SensorView.vue';
import { onUnmounted, reactive, ref, shallowRef, triggerRef, type Ref, type ShallowRef } from 'vue'
import type { SensorData } from './sensorData'

type ConnectionState = 'connecting' | 'open' | 'error' | 'closed'

const connectionState = ref<ConnectionState>('connecting')
const sensorMap = shallowRef(new Map<string, SensorData>())
const sensorOrder: Ref<string[]> = ref([])

const scheduledRefTriggers = new Set<ShallowRef<any>>()
function scheduleRefTrigger(ref: ShallowRef) {
  if (scheduledRefTriggers.has(ref)) {
    return
  }
  scheduledRefTriggers.add(ref)
  requestAnimationFrame(() => {
    scheduledRefTriggers.delete(ref)
    triggerRef(ref)
  })
}

function onOpen(e: Event) {
  connectionState.value = 'open';
}
function onClose(e: Event) {
  if (connectionState.value != 'error') {
    connectionState.value = 'closed';
  }
}
function onError(e: Event) {
  connectionState.value = 'error';
}
function onMessage(e: MessageEvent) {
  const message = JSON.parse(e.data)
  const id: string = message["id"]
  const packets = message["packet"]

  if (!sensorMap.value.has(id)) {
    console.log("New sensor", id)
    sensorMap.value.set(id, {
      id, packets: shallowRef(new Array())
    })

    sensorOrder.value.push(id)
    sensorOrder.value.sort()
    scheduleRefTrigger(sensorMap.value.get(id)!.packets)
    scheduleRefTrigger(sensorMap)
  }
  const sensorData = sensorMap.value.get(id)!

  sensorData.packets.value.push(packets)
  scheduleRefTrigger(sensorData.packets)
}

// TODO: Configure url or host on same port as client
const connection = new WebSocket('ws://127.0.0.1:5000/ws')

connection.addEventListener('open', onOpen)
connection.addEventListener('close', onClose)
connection.addEventListener('error', onError)
connection.addEventListener('message', onMessage)

onUnmounted(() => {
  console.log("App unmounted, closing existing connection")
  connection.removeEventListener('open', onOpen)
  connection.removeEventListener('close', onClose)
  connection.removeEventListener('error', onError)
  connection.removeEventListener('message', onMessage)
  connection.close()
})
</script>

<template>
  <header>
    <StatusHeader v-if="connectionState == 'connecting'" title="Connecting to server..." />
    <StatusHeader v-if="connectionState == 'closed'" title="Connection closed by server" />
    <StatusHeader v-if="connectionState == 'error'" title="Error connecting to server" />
    <StatusHeader v-if="connectionState == 'open'" title="Connected to server" />
  </header>

  <main v-if="connectionState == 'open'">
    <template v-for="sensorId in sensorOrder" :key="sensorId">
      <hr>
      <SensorView :data="sensorMap.get(sensorId)!"></SensorView>
    </template>
    <hr>
    <h1 v-if="sensorOrder.length == 0">Waiting for data...</h1>
</main>
</template>

<style scoped>
hr {
  border: 2px solid var(--color-border);
}
</style>
