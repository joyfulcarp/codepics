<template>
  <div v-if="game != null">
    <Team
      :team="'blue'"
      :info="game.teams['blue']"
      @join-team="events.joinTeam(props.gameId, 'blue')" />
    <Team
      :team="'red'"
      :info="game.teams['red']"
      @join-team="joinTeam(props.gameId, 'red')" />
  </div>
</template>

<script setup lang="ts">
import Team from '@/components/Team.vue'

import type { GameState } from '@/assets/ts/game.ts'
import { GameEvents } from '@/assets/ts/game.ts'

import {
  ref,
  watch,
  onMounted,
  onUnmounted
} from 'vue'

const props = defineProps({
  name: String,
  gameId: Number
})

const game: GameState = ref(null)
const events = new GameEvents('http://localhost:5001', game)

onMounted(() => {
  if (props.name != null && props.gameId != null) {
    events.join(props.gameId, props.name)
  }
})

watch(props.gameId, (newId, oldId) => {
  events.leave(oldId)
  game.value = null
  events.join(newId, props.name)
})

onUnmounted(() => {
  if (props.gameId != null) {
    events.leave(props.gameId)
  }
})
</script>
