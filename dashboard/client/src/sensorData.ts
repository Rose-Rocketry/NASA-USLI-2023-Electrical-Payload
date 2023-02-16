import type { ShallowRef } from "vue"

export type SensorData = {
  "id": string,
  "packets": ShallowRef<any[]>
}

export type ChannelType = "vector" | "number" | "boolean" | "string" | "unknown"
