<template>
  <div class="content">
    <div class="player-info">
      <input id="player-name" v-model="new_name" placeholder="Enter your name" />
      <button class="button" @click="updateName()">Update Name</button>
    </div>

    <div v-if="game != null" class="game-ui">
      <Team
        :team="blue"
        :info="blueTeam"
        @join-team="events.joinTeam(gameId, blue, false)"
        @join-spymaster="events.joinTeam(gameId, blue, true)"
        class="blue-team-info" />
      <Team
        :team="red"
        :info="redTeam"
        @join-team="events.joinTeam(gameId, red, false)"
        @join-spymaster="events.joinTeam(gameId, red, true)"
        class="red-team-info" />
      <HintBar
        :events="events"
        :game-id="gameId"
        :is-active-team="isActiveTeam"
        :is-spymaster="isSpymaster"
        :is-spymaster-turn="isSpymasterTurn"
        :supplied-hint="game.hint"
        class="hint-bar" />

      <div class="game-info">
        <div class="game-info-container">
          <History :history="game.history" class="history" />
          <img v-show="showPreviewImg" class="preview-image" :src="previewImgSrc" />
        </div>
      </div>

      <div class="game-board">
        <div v-if="!isMatchmaking">
          <Cards
            :events="events"
            :base-url="imgUrl"
            :collection="game.collection"
            :game-id="gameId"
            :cards="game.cards"
            :votes="game.votes"
            :current-team="currentTeam"
            :allow-actions="allowCardActions"
            @preview-image="previewImage"
            @leave-image="leaveImage" />
        </div>
        <div v-else>
          <Host
            v-if="isHost && isMatchmaking"
            :events="events"
            :game-id="gameId" />
        </div>
      </div>
    </div>

    <!-- Else: game == null -->
    <div v-else class="game-connect-error">
      <h1>Error 404: Invalid lobby</h1>
      <p>Please return to homepage and create a new room.</p>
    </div>

    <Debug
      v-if="isDebug && game != null"
      :events="events"
      :game-id="gameId"
      :game="game" />
  </div>
</template>

<script setup lang="ts">
import Cards from '@/components/Cards.vue'
import Debug from '@/components/Debug.vue'
import HintBar from '@/components/HintBar.vue'
import History from '@/components/History.vue'
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
import { useRoute } from 'vue-router'

const route = useRoute()
const gameId = ref(null)
watch(() => route.params.id, (newId, oldId) => {
  if (oldId === newId) return

  const parsed = parseInt(newId)
  if (Number.isNaN(parsed)) {
    gameId.value = null
    return
  }

  gameId.value = parsed
}, {immediate: true})

onMounted(() => {
  if (name.value != null && gameId.value != null) {
    events.join(gameId.value, name.value)
  }
})

watch(() => gameId, (newId, oldId) => {
  events.leave(oldId)
  game.value = null
  events.join(newId, name.value)
})

onUnmounted(() => {
  if (gameId.value != null) {
    events.leave(gameId.value)
  }
})

const isDebug = import.meta.env.DEV

const name = ref('Test')
//const name = ref(null)
const new_name = ref(null)

const game: GameState = ref(null)
const isHost = ref(false)
const previewImgSrc = ref('')

const url = getUrl()
const imgUrl = url + 'static/cards/'
const events = new GameEvents(url, game, isHost)

const blue = 'blue'
const red = 'red'

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

const isSpymasterTurn = computed(() => {
  return game.value.play_state == 'red_spymaster' || game.value.play_state == 'blue_spymaster'
})

const isActiveTeam = computed(() => {
  return selfTeam.value == currentTeam.value
})

const allowCardActions = computed(() => {
  return !isSpymaster.value && isActiveTeam.value && !isSpymasterTurn.value
})

const showPreviewImg = computed(() => {
  return previewImgSrc.value && previewImgSrc.value != ''
})

function updateName() {
  name.value = new_name.value
}

function previewImage(url: String) {
  previewImgSrc.value = url
}

function leaveImage() {
  previewImgSrc.value = ''
}

function isSpymasterForTeam(team) {
  if (!team || !team['spymaster']) return false
  else return team['spymaster']['is_self'] == true
}

function isInTeam(team) {
  return isSpymasterForTeam(team) || team['agents'].some(player => { return player['is_self'] })
}
</script>

<style scoped>
.content {
  position: relative;
  background-color: green;
  width: 100vw;
  height: 100vh;

  display: grid;
  grid-template-rows: min-content min-content min-content 1fr;
  grid-template-columns: 1fr 1fr 3fr;
  gap: 10px;
}

.player-info {
  grid-row: 1;
  grid-column: 1 / span 2;
}

.game-connect-error {
  grid-row: 2 / span 3;
  grid-column: 1 / span 3;
}

.game-ui {
  grid-row: 2 / span 3;
  grid-column: 1 / span 3;

  display: grid;
  grid-template-rows: subgrid;
  grid-template-columns: subgrid;
}

.blue-team-info {
  grid-row: 1;
  grid-column: 1;
}

.red-team-info {
  grid-row: 1;
  grid-column: 2;
}

.hint-bar {
  grid-row: 2;
  grid-column: 1 / span 2;
}

.game-info {
  grid-row: 3;
  grid-column: 1 / span 2;
}

.game-info-container {
  display: grid;
  grid-template-rows: 1fr;
  grid-template-columns: 1fr;

  width: 100%;
  height: 100%;
  contain: size;
}

.history {
  grid-row: 1;
  grid-column: 1;

  z-index: 1;
  width: 100%;
  height: 100%;
}

.preview-image {
  grid-row: 1;
  grid-column: 1;

  z-index: 2;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: white;
  border-radius: 10px;
}

.game-board {
  grid-row: 1 / span 3;
  grid-column: 3;
}
</style>
