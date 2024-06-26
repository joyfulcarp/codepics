<template>
  <div class="board" @mouseleave="$emit('leaveImage')">
    <template v-for="(card, index) in props.cards" :key="index">
      <div
          class="card"
          :card="[cardTeams[index]]"
          @mouseover="$emit('previewImage', imgs[index])">
        <img :class="['image', cardTeams[index]]" :src="imgs[index]" />
        <button v-show="actions[index]" class="vote button" @click="events.vote(props.gameId, index)">Vote</button>
        <button v-show="actions[index]" class="reveal alt-button" @click="events.reveal(props.gameId, index)">Reveal</button>
        <p class="vote-list" v-if="props.votes[index]">
          <span class="name" v-for="player in props.votes[index]">{{ player }}</span>
        </p>
        <div v-if="card.hidden === false" class="cover" :class="[cardTeams[index]]">
          <p>{{ index }}</p>
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

const actions = computed(() => {
  let act = []
  for (const card of props.cards) {
    if (!props.allowActions)
      act.push(false)
    else if (card.hidden == undefined || card.hidden == null)
      act.push(true)
    else if (card.hidden == false)
      act.push(false)
    else
      act.push(true)
  }
  return act
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
  width: 100%;
  height: 100%;
}

.card {
  display: grid;
  grid-template-rows: min-content 1fr;
  grid-template-columns: 1fr 1fr;

  contain: size;
  border-radius: 10px;
}

.red-card {
  border-width: 10px;
  border-style: solid;
  border-color: #e55731;

  &.cover {
    background-color: #e55731;
  }
}

.blue-card {
  border-width: 10px;
  border-style: solid;
  border-color: #3284a3;

  &.cover {
    background-color: #3284a3;
  }
}

.innocent-card {
  border-width: 10px;
  border-style: solid;
  border-color: #f3d8b5;

  &.cover {
    background-color: #f3d8b5;
  }
}

.assassin-card {
  border-width: 20px;
  border-style: solid;
  border-color: black;

  &.cover {
    background-color: black;
  }
}

.image {
  grid-row: 1 / span 2;
  grid-column: 1 / span 2;

  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.vote {
  grid-row: 1;
  grid-column: 1;
  justify-self: start;

  z-index: 2;
  margin: 5px;
}

.reveal {
  grid-row: 1;
  grid-column: 2;
  justify-self: end;

  z-index: 2;
  margin: 5px;
}

.vote-list {
  grid-row: 2;
  grid-column: 1 / span 2;

  z-index: 2;
  width: 100%;
  max-height: 100%;
  overflow: auto;
}

.name {
  display: inline-block;
  margin: 5px;
  padding: 5px;
  height: min-content;
  color: white;
  background-color: v-bind('bgColor');
}

.cover {
  grid-row: 1 / span 2;
  grid-column: 1 / span 2;

  z-index: 3;
  width: 100%;
  height: 100%;
  border-radius: 10px;

  display: flex;
  justify-content: center;
  align-items: center;
}

.cover p {
  color: white;
  font-size: 4em;
  text-align: center;
}
</style>
