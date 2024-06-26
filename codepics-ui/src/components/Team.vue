<template>
  <div class="info">
    <div class="card-count">{{ info['cards_left'] }}</div>
    <p class="spymaster-text role-text">Spymaster</p>
    <div class="spymaster-info">
      <p v-if="spymaster" class="name" :class="{ 'self-name': spymaster['is_self'] }">{{ spymaster['name'] }}</p>
      <button class="button" v-if="showJoinSpymaster" @click="$emit('joinSpymaster')">Join as Spymaster</button>
    </div>
    <p class="agents-text role-text">Agents</p>
    <button class="agents-button button" v-if="showJoinAgents" @click="$emit('joinTeam')">Join as Agent</button>
    <div class="agents-list">
      <p v-for="player in agents" class="name" :class="{ 'self-name': player['is_self'] }">{{ player['name'] }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

defineEmits(['joinTeam', 'joinSpymaster'])

const props = defineProps({
  team: String,
  info: Object,
  allowArbitrarySwaps: Boolean,
  selfTeam: String,
  isSpymaster: Boolean
})

const spymaster = computed(() => { return props.info['spymaster'] })
const agents = computed(() => { return props.info['agents'] })

const isSelfInAgents = computed(() => {
  return props.info['agents'].some(player => { return player['is_self'] })
})

const showJoinSpymaster = computed(() => {
  if (spymaster.value) return false
  else if (!props.selfTeam) return true
  else if (props.allowArbitrarySwaps) return true
  else return props.team == props.selfTeam
})

const showJoinAgents = computed(() => {
  if (isSelfInAgents.value) return false
  else if (props.allowArbitrarySwaps) return true
  else if (!props.selfTeam) return true
  else if (props.isSpymaster) return false
  else return props.team == props.selfTeam
})

const redColors = {
  'bg': '#8f2b1c',
  'role-text': '#e55731'
}
const blueColors = {
  'bg': '#3284a3',
  'role-text': '#7ac9e8'
}

const colors = computed(() => {
  return props.team == 'blue' ? blueColors : redColors
})
</script>

<style scoped>
p {
  margin: 0;
}

.name {
  display: inline-block;
  font-weight: normal;
  padding: 1px 5px;
  color: white;
}

.self-name {
  font-weight: bold;
  font-style: italic;
}

.role-text {
  color: v-bind("colors['role-text']");
  font-weight: bold;
}

.info {
  padding: 10px;
  display: grid;
  grid-template-rows: min-content 30px 30px min-content;
  grid-template-columns: min-content 1fr;
  gap: 5px 10px;
  align-items: center;
  min-width: 0;
  min-height: 0;
  background-color: v-bind("colors['bg']");
  border-radius: 10px;
}

.card-count {
  grid-row: 1 / span 2;
  grid-column: 1;
  min-width: 0;
  min-height: 0;
  justify-self: center;
  font-weight: bold;
  font-size: 3em;
  color: white;
  text-shadow: black 1px 0 20px;
}

.spymaster-text {
  grid-row: 1;
  grid-column: 2;
  min-width: 0;
  min-height: 0;
}

.spymaster-info {
  grid-row: 2;
  grid-column: 2;
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.spymaster-info * {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.agents-text {
  grid-row: 3;
  grid-column: 1;
  min-width: 0;
  min-height: 0;
}

.agents-button {
  grid-row: 3;
  grid-column: 2;
  min-width: 0;
  min-height: 0;
}

.agents-list {
  grid-row: 4;
  grid-column: 1 / span 2;
  align-self: start;
  min-width: 0;
  height: 3em;
  overflow: auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
}
</style>
