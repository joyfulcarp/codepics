<template>
  <div class="board" @mouseleave="$emit('leaveImage')">
    <template v-for="(card, index) in props.cards" :key="index">
      <div
          class="card"
          :id="`card-${index}`"
          @mouseover="$emit('previewImage', imgs[index])">
        <img :class="['image', cardTeams[index]]" :src="imgs[index]" />
        <button v-show="props.allowActions" class="vote button" @click="events.vote(props.gameId, index)">Vote</button>
        <button v-show="props.allowActions" class="reveal alt-button" @click="events.reveal(props.gameId, index)">Reveal</button>
        <div class="vote-list" v-if="props.votes[index]">
          <p class="name" v-for="player in props.votes[index]">{{ player }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { GameEvents } from '@/assets/ts/game.ts'

import { computed } from 'vue'

defineEmits(['previewImage', 'leaveImage'])

const props = defineProps({
  events: GameEvents,
  baseUrl: String,
  collection: String,
  gameId: Number,
  cards: Object,
  votes: Object,
  currentTeam: String,
  allowActions: Boolean
})

const imgs = computed(() => {
  let links = []
  for (const card of props.cards) {
    links.push(props.baseUrl + props.collection + '/' + card['asset'])
  }
  return links
})

const bgColor = computed(() => {
  if (props.currentTeam == 'blue')
    return 'blue'
  else if (props.currentTeam == 'red')
    return 'red'
  else
    return 'black'
})

const cardTeams = computed(() => {
  let classes = []
  for (const card of props.cards) {
    if (card['team'] == 'blue')
      classes.push('blue-card')
    else if (card['team'] == 'red')
      classes.push('red-card')
    else if (card['team'] == 'innocent')
      classes.push('innocent-card')
    else if (card['team'] == 'assassin')
      classes.push('assassin-card')
    else
      classes.push('')
  }
  return classes
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
  grid-template-rows: min-content 1fr;
  grid-template-columns: 1fr 1fr;
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
  object-fit: contain;
  box-sizing: border-box;
  border-radius: 10px;
}

.red-card {
  border: 5px solid red;
}

.blue-card {
  border: 5px solid blue;
}

.innocent-card {
  border: 5px solid #f3d8b5;
}

.assassin-card {
  border: 5px solid black;
}

.vote {
  z-index: 2;
  grid-row: 1;
  grid-column: 1;
  margin: 5px;
}

.reveal {
  z-index: 2;
  grid-row: 1;
  grid-column: 2;
  margin: 5px;
}

.vote-list {
  z-index: 2;
  grid-row: 2;
  grid-column: 1 / span 2;
  width: 100%;
  height: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  overflow: auto;
  contain: size;
}

p {
  margin: 0;
}

.name {
  display: inline-block;
  font-weight: normal;
  padding: 1px 5px;
  color: white;
  background-color: v-bind('bgColor');
  height: min-content;
  margin-left: 5px;
  margin-right: 5px;
}
</style>
