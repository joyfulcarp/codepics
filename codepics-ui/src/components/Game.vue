<template>
  <div v-if="game != null">
    <Team
      :team="blue"
      :info="game.teams[blue]"
      @join-team="events.joinTeam(props.gameId, blue, false)"
      @join-spymaster="events.joinTeam(props.gameId, blue, true)" />
    <Team
      :team="red"
      :info="game.teams[red]"
      @join-team="events.joinTeam(props.gameId, red, false)"
      @join-spymaster="events.joinTeam(props.gameId, red, true)" />

    <div v-if="isGameInProgress">
      <Cards
        :events="events"
        :base-url="imgUrl"
        :collection="game.collection"
        :game-id="props.gameId"
        :cards="game.cards" />
    </div>
    <div v-else>
      <Host
        v-if="showHostSetup"
        :events="events"
        :game-id="props.gameId" />
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
import Cards from '@/components/Cards.vue'
import Host from '@/components/Host.vue'
import Team from '@/components/Team.vue'

import type { GameState } from '@/assets/ts/game.ts'
import { GameEvents } from '@/assets/ts/game.ts'
import { getUrl } from '@/assets/ts/query.ts'

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
const isHost = ref(false)

const url = getUrl()
const imgUrl = url + 'static/cards/'
const events = new GameEvents(url, game, isHost)

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

const showHostSetup = computed(() => {
  return isHost && game.value.play_state == 'matchmaking'
})

const isGameInProgress = computed(() => {
  return game.value.play_state != 'matchmaking'
})

onUnmounted(() => {
  if (props.gameId != null) {
    events.leave(props.gameId)
  }
})
</script>
