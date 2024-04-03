<template>
  <div>{{ info['cards_left'] }}</div>
  <div>
    <h2>Agents</h2>
    <span v-for="player in info['agents']">{{ player.name }}</span>
  </div>
  <div>
    <h2>Spymaster</h2>
    <span v-if="info['spymaster']">{{ info['spymaster'].name }}</span>
  </div>
  <div>
    <button @click="$emit('joinTeam')">Join as Agent</button>
    <button v-if="!info['spymaster']" @click="$emit('joinSpymaster')">Join as Spymaster</button>
  </div>
</template>

<script setup lang="ts">
defineEmits(['joinTeam', 'joinSpymaster'])

const props = defineProps({
  team: String,
  info: Object
})
</script>
