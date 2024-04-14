<template>
  <div class="host-options">
    <label for="card-packs">Choose card pack:</label>
    <select id="card-packs">
      <option v-for="pack in cardPacks" :value="pack">{{ pack }}</option>
    </select>
    <button class="button" @click="events.startGame(props.gameId)">Start Game</button>
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

<style scoped>
select {
  padding: 10px;
  font-weight: bold;
  border-style: none;
  border-radius: 5px;
}

.host-options {
  padding: 10px;
  background-color: white;

  display: flex;
  align-content: flex-start;
  align-items: center;
  gap: 10px;
}
</style>
