<template>
  <div>
    <label for="card_packs">Choose card pack:</label>
    <select id="card_packs">
      <option v-for="pack in cardPacks" :value="pack">{{ pack }}</option>
    </select>
    <button @click="events.startGame(props.gameId)">Start Game</button>
  </div>
</template>

<script setup lang="ts">
import { getCardCollections } from '@/assets/ts/query.ts'
import { GameEvents } from '@/assets/ts/game.ts'

import { ref } from 'vue'

const props = defineProps({
  events: GameEvents,
  gameId: Number
})

const cardPacks = ref([])
getCardCollections()
  .then((res) => { cardPacks.value = res.data.collections })
  .catch(console.error)
</script>
