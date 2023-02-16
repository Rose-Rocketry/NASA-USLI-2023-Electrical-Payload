<script setup lang="ts">
defineProps({
  title: String,
  spinner: Boolean
})
</script>

<template>
  <h1 class="green">{{title}}</h1>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
}
</style>
