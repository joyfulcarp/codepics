<template>
  <div>{{ info.cards }}</div>
  <div>
    <span v-for="player in info.members">{{ player }}</span>
  </div>
  <div>
    <button @click="$emit('joinTeam')">Join</button>
  </div>
</template>

<script setup>
defineEmits(['joinTeam'])

const props = defineProps({
  team: String,
  info: Object
})
</script>
