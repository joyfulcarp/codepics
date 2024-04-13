<template>
  <div v-if="game != null">
    <div class="ui">
      <div class="game-info">
        <div class="game-info-container">
          <img class="preview-image" :src="previewImgSrc" />
        </div>
      </div>
      <Team
        :team="blue"
        :info="blueTeam"
        @join-team="events.joinTeam(props.gameId, blue, false)"
        @join-spymaster="events.joinTeam(props.gameId, blue, true)"
        class="blue-team-info" />
      <Team
        :team="red"
        :info="redTeam"
        @join-team="events.joinTeam(props.gameId, red, false)"
        @join-spymaster="events.joinTeam(props.gameId, red, true)"
        class="red-team-info" />

      <div class="game">
        <div v-if="!isMatchmaking">
          <Cards
            :events="events"
            :base-url="imgUrl"
            :collection="game.collection"
            :game-id="props.gameId"
            :cards="game.cards"
            :votes="game.votes"
            :current-team="currentTeam"
            :allow-actions="allowActions"
            @preview-image="previewImage"
            @leave-image="leaveImage" />
        </div>
        <div v-else>
          <Host
            v-if="isHost && isMatchmaking"
            :events="events"
            :game-id="props.gameId" />
        </div>
      </div>
    </div>

    <div v-show="is_debug">
      <h2>Debug</h2>
      <p>{{ game.play_state ? game.play_state : '' }}</p>
      <button @click="events.debug_fill(props.gameId)">Fill Game</button>
      <button @click="events.debug_leave_all()">Leave All</button>
      <div>
        <input v-model="debug_info.hint" placeholder="Enter your hint" />
        <select v-model="debug_info.count">
          <option v-for="i in 10">{{ i - 1 }}</option>
        </select>
        <button @click="events.debug_give_hint(props.gameId, debug_info.hint, debug_info.count)">Go</button>
      </div>
      <div>
        <select v-model="debug_info.card">
          <option v-for="i in 20">{{ i - 1 }}</option>
        </select>
        <button @click="events.debug_vote(props.gameId, debug_info.card)">Vote</button>
        <button @click="events.debug_reveal(props.gameId, debug_info.card)">Reveal</button>
        <button @click="events.debug_end_guessing(props.gameId)">End Guessing</button>
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
const debug_info = ref({'hint': 'Test hint', 'count': 0, 'card': 0})

const game: GameState = ref(null)
const isHost = ref(false)
const previewImgSrc = ref('')

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

const isMatchmaking = computed(() => {
  return game.value.play_state == 'matchmaking'
})

const currentTeam = computed(() => {
  if (game.value.play_state == 'red_spymaster' || game.value.play_state == 'red_agents')
    return red
  else if (game.value.play_state == 'blue_spymaster' || game.value.play_state == 'blue_agents')
    return blue
  else
    return 'unknown'
})

const blueTeam = computed(() => { return game.value.teams[blue] })
const redTeam = computed(() => { return game.value.teams[red] })

const selfTeam = computed(() => {
  if (isInTeam(blueTeam.value)) return blue
  else if (isInTeam(redTeam.value)) return red
  else return ''
})

const isSpymaster = computed(() => {
  return isSpymasterForTeam(blueTeam.value) || isSpymasterForTeam(redTeam.value)
})

const allowActions = computed(() => {
  return !isSpymaster.value && selfTeam.value == currentTeam.value
})

onUnmounted(() => {
  if (props.gameId != null) {
    events.leave(props.gameId)
  }
})

function previewImage(url: String) {
  previewImgSrc.value = url
}

function leaveImage() {
  previewImgSrc.value = ''
}

function isSpymasterForTeam(team) {
  return team['spymaster']['is_self']
}

function isInTeam(team) {
  return isSpymasterForTeam(team) || team['agents'].some(player => { return player['is_self'] })
}
</script>

<style scoped>
.ui {
  display: grid;
  grid-template-rows: min-content 2fr;
  grid-template-columns: 1fr 1fr 3fr;
  gap: 10px;
  min-width: 0;
  min-height: 0;
}

.game-info {
  grid-row: 2;
  grid-column: 1 / span 2;
  min-width: 0;
  min-height: 0;
  contain: size;
}

.game-info-container {
  display: grid;
  grid-template-rows: 1fr;
  grid-template-columns: 1fr;
  min-width: 0;
  min-height: 0;
  width: 100%;
  height: 100%;
  contain: size;
}

.preview-image {
  grid-row: 1;
  grid-column: 1;
  min-width: 0;
  min-height: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.blue-team-info {
  grid-row: 1;
  grid-column: 1;
}

.red-team-info {
  grid-row: 1;
  grid-column: 2;
}

.game {
  grid-row: 1 / span 2;
  grid-column: 3;
  min-width: 0;
  min-height: 0;
}
</style>
