<template>
  <div>
    <div>{{ info['cards_left'] }}</div>
    <div>
      <h2>Agents</h2>
      <span v-for="player in agents" class="name" :class="{ 'self-name': player['is_self'] }">{{ player['name'] }}</span>
    </div>
    <div>
      <h2>Spymaster</h2>
      <span v-if="spymaster" class="name" :class="{ 'self-name': spymaster['is_self'] }">{{ spymaster['name'] }}</span>
    </div>
    <div>
      <button v-if="!isSelfInAgents" @click="$emit('joinTeam')">Join as Agent</button>
      <button v-if="!spymaster" @click="$emit('joinSpymaster')">Join as Spymaster</button>
    </div>
  </div>
</template>

<style scoped>
.name {
  display: block;
  font-weight: normal;
  color: white;
  background-color: v-bind('bgColor');
}

.self-name {
  font-weight: bold;
}
</style>

<script setup lang="ts">
import { computed } from 'vue'

defineEmits(['joinTeam', 'joinSpymaster'])

const props = defineProps({
  team: String,
  info: Object
})

const spymaster = computed(() => { return props.info['spymaster'] })
const agents = computed(() => { return props.info['agents'] })

const isSelfInAgents = computed(() => {
  return props.info['agents'].some(player => { return player['is_self'] })
})

const bgColor = computed(() => {
  return props.team == 'blue' ? 'blue' : 'red'
})
</script>
