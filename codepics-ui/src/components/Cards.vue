<template>
  <div class="board">
    <template v-for="(card, index) in props.cards" :key="index">
      <div class="card" :id="`card-${index}`">
        <img class="image" :src="imgs[index]" />
        <button class="vote" @click="events.vote(props.gameId, index)">Vote</button>
        <button class="reveal" @click="events.reveal(props.gameId, index)">Reveal</button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { GameEvents } from '@/assets/ts/game.ts'

import { computed } from 'vue'

const props = defineProps({
  events: GameEvents,
  baseUrl: String,
  collection: String,
  gameId: Number,
  cards: Object
})

const imgs = computed(() => {
  let links = []
  for (const card of props.cards) {
    links.push(props.baseUrl + props.collection + '/' + card['asset'])
  }
  return links
})
</script>

<style scoped>
.board {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  min-width: 0;
  min-height: 0;
}

.card {
  display: grid;
  grid-template-rows: 30px 1fr;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  place-items: center;
  min-width: 0;
  min-height: 0;
}

.image {
  z-index: 1;
  grid-row: 1 / span 2;
  grid-column: 1 / span 2;
  min-width: 0;
  min-height: 0;
  width: 100%;
  height: 100%;
}

.vote {
  z-index: 2;
  grid-row: 1;
  grid-column: 1;
}

.reveal {
  z-index: 2;
  grid-row: 1;
  grid-column: 2;
}
</style>
