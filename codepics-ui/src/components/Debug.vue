<template>
  <div class="debug">
    <h2>Debug</h2>
    <p>{{ props.game.play_state ? props.game.play_state : '' }}</p>
    <button @click="events.debug_fill(props.gameId)">Fill Game</button>
    <button @click="events.debug_leave_all()">Leave All</button>
    <div>
      <input v-model="debugInfo.hint" placeholder="Enter your hint" />
      <select v-model="debugInfo.count">
        <option v-for="i in 10">{{ i - 1 }}</option>
      </select>
      <button @click="events.debug_give_hint(props.gameId, debugInfo.hint, debugInfo.count)">Go</button>
    </div>
    <div>
      <select v-model="debugInfo.card">
        <option v-for="i in 20">{{ i - 1 }}</option>
      </select>
      <button @click="events.debug_vote(props.gameId, debugInfo.card)">Vote</button>
      <button @click="events.debug_reveal(props.gameId, debugInfo.card)">Reveal</button>
      <button @click="events.debug_end_guessing(props.gameId)">End Guessing</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GameState } from '@/assets/ts/game.ts'
import { GameEvents } from '@/assets/ts/game.ts'

import { ref } from 'vue'

const props = defineProps({
  events: GameEvents,
  gameId: Number,
  game: Object
})

const debugInfo = ref({'hint': 'Test hint', 'count': 0, 'card': 0})
</script>

<style scoped>
.debug {
  z-index: 99;
  position: absolute;
  bottom: 0;
  background-color: white;
}
</style>
