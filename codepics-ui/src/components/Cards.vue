<template>
  <div>
    <template v-for="(card, index) in props.cards" :key="index">
      <div>
        <img :src="imgs[index]" />
        <button @click="events.vote(props.gameId, index)">Vote</button>
        <button @click="events.reveal(props.gameId, index)">Reveal</button>
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
