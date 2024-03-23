<template>
  <div>{{ cards }}</div>
  <div>
    <h2>Agents</h2>
    <span v-for="player in info['agents'].filter(p => p != info['spymaster'])">{{ player }}</span>
  </div>
  <div>
    <h2>Spymaster</h2>
    <span>{{ info['spymaster'] }}</span>
  </div>
  <div>
    <button @click="$emit('joinTeam')">Join as Agent</button>
    <button v-if="!info['spymaster']" @click="$emit('joinSpymaster')">Join as Spymaster</button>
  </div>
</template>

<script setup>
defineEmits(['joinTeam', 'joinSpymaster'])

const props = defineProps({
  team: String,
  info: Object,
  cards: String
})
</script>
