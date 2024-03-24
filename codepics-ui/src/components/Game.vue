<template>
  <div v-if="game != null">
    <Team
      :team="blue"
      :info="game.teams[blue]"
      :cards="blue_cards"
      @join-team="events.joinTeam(props.gameId, blue, false)"
      @join-spymaster="events.joinTeam(props.gameId, blue, true)" />
    <Team
      :team="red"
      :info="game.teams[red]"
      :cards="red_cards"
      @join-team="events.joinTeam(props.gameId, red, false)"
      @join-spymaster="events.joinTeam(props.gameId, red, true)" />

    <div v-if="is_host">
      <label for="card_packs">Choose card pack:</label>
      <select id="card_packs">
        <option v-for="pack in cardPacks" :value="pack">{{ pack }}</option>
      </select>
      <button @click="events.startGame(props.gameId)">Start Game</button>
    </div>

    <div v-show="is_debug">
      <h2>Debug</h2>
      <button @click="events.debug_fill(props.gameId)">Fill Game</button>
      <button @click="events.debug_leave_all()">Leave All</button>
      <div>
        <input v-model="debug_info.hint" placeholder="Enter your hint" />
        <select v-model="debug_info.count">
          <option v-for="i in 10">{{ i - 1 }}</option>
        </select>
        <button @click="events.debug_give_hint(props.gameId, debug_info.hint, debug_info.count)">Go</button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Invalid game ID</p>
  </div>
</template>

<script setup lang="ts">
import Team from '@/components/Team.vue'

import type { GameState } from '@/assets/ts/game.ts'
import { GameEvents } from '@/assets/ts/game.ts'
import { getUrl, getCardCollections } from '@/assets/ts/query.ts'

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

const is_debug = import.meta.env.DEV
const debug_info = ref({'hint': '', 'count': 0})

const game: GameState = ref(null)
const is_host = ref(false)
const events = new GameEvents(getUrl(), game, is_host)

const cardPacks = ref([])
getCardCollections()
  .then((res) => { cardPacks.value = res.data.collections })
  .catch(console.error)

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
