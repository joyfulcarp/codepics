<template>
  <div v-if="game != null">
    <Team
      :team="blue"
      :info="game.teams[blue]"
      :cards="blue_cards"
      @join-team="events.joinTeam(props.gameId, blue)"
      @join-spymaster="events.joinTeam(props.gameId, blue, True)" />
    <Team
      :team="red"
      :info="game.teams[red]"
      :cards="red_cards"
      @join-team="events.joinTeam(props.gameId, red)"
      @join-spymaster="events.joinTeam(props.gameId, red, True)" />
    <div>
      <button @click="events.startGame(props.gameId)">Start Game</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import Team from '@/components/Team.vue'

import type { GameState } from '@/assets/ts/game.ts'
import { GameEvents } from '@/assets/ts/game.ts'

import {
  computed,
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

const blue = 'blue'
const red = 'red'

onMounted(() => {
  if (props.name != null && props.gameId != null) {
    events.join(props.gameId, props.name)
  }
})

watch(() => props.gameId, (newId, oldId) => {
  events.leave(oldId)
  game.value = null
  events.join(newId, props.name)
})

function countCards(cards, team): string {
  if (!cards) return '-'
  else return cards.filter(card => card['team'] == team)
}

// const blue_cards = computed(() => countCards(game.value['cards'], 'blue'))
// const red_cards = '-'
const blue_cards = '-'
const red_cards = '-'

onUnmounted(() => {
  if (props.gameId != null) {
    events.leave(props.gameId)
  }
})
</script>
