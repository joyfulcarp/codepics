<template>
  <div class="content">
    <div class="player-info">
      <input class="player-name" v-model="new_name" placeholder="ENTER YOUR NAME" />
      <button class="button" @click="updateName()">Update Name</button>
    </div>
    <div class="message-info">
      <p v-if="message != ''" class="message">{{ message }}</p>
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
          <History :history="game.history" :winner="winner" class="history" />
          <img v-show="showPreviewImg" class="preview-image" :src="previewImgSrc" />
        </div>
      </div>

      <div v-if="!isMatchmaking" class="game-board">
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
      <div v-else class="game-board">
        <Host
          v-if="isHost && isMatchmaking"
          :events="events"
          :game-id="gameId" />
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

const blueTeam = computed(() => { return game.value ? game.value.teams[blue] : null })
const redTeam = computed(() => { return game.value ? game.value.teams[red] : null })

const selfTeam = computed(() => {
  if (isInTeam(blueTeam.value)) return blue
  else if (isInTeam(redTeam.value)) return red
  else return ''
})

const isSpymaster = computed(() => {
  return isSpymasterForTeam(blueTeam.value) || isSpymasterForTeam(redTeam.value)
})

const isSpymasterTurn = computed(() => {
  if (!game.value) return false
  return game.value.play_state == 'red_spymaster' || game.value.play_state == 'blue_spymaster'
})

const isActiveTeam = computed(() => {
  return selfTeam.value == currentTeam.value
})

const allowCardActions = computed(() => {
  return !isSpymaster.value && isActiveTeam.value && !isSpymasterTurn.value
})

const winner = computed(() => {
  if (!game.value.winner) return null
  else if (game.value.winner == blue) return blue
  else if (game.value.winner == red) return red
  else return null
})

const bgColor = computed(() => {
  const blueBg = '#084059'
  const redBg = '#501005'
  const neutral = 'black'
  const colors = {
    'blue_spymaster': blueBg,
    'blue_agents': blueBg,
    'red_spymaster': redBg,
    'red_agents': redBg
  }

  if (!game.value) return neutral
  const turnColor = colors[game.value.play_state]
  if (!turnColor) return neutral
  else return turnColor
})

const showPreviewImg = computed(() => {
  return previewImgSrc.value && previewImgSrc.value != ''
})

const message = computed(() => {
  name.value
  if (name.value == '')
    return 'Enter your name.'
  else if (!game.value)
    return ''
  else if (selfTeam.value == '')
    return 'Join a team.'
  else if (isMatchmaking.value)
    return 'Waiting for game to start...'
  else if (!isActiveTeam.value && isSpymasterTurn.value)
    return 'The opponent spymaster is playing, wait for your turn...'
  else if (!isActiveTeam.value && !isSpymasterTurn.value)
    return 'The opponent agents are playing, wait for your turn...'
  else if (isSpymaster.value && isSpymasterTurn.value)
    return 'Give your agents a clue.'
  else if (isSpymaster.value && !isSpymasterTurn.value)
    return 'Your agents are guessing now...'
  else if (!isSpymaster.value && isSpymasterTurn.value)
    return 'Wait for your spymaster to give a clue...'
  else if (!isSpymaster.value && !isSpymasterTurn.value)
    return 'Try to guess a word.'
  else if (winner.value && winner.value == 'blue')
    return 'Blue team wins!'
  else if (winner.value && winner.value == 'red')
    return 'Red team wins!'
  else
    return ''
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
  if (isSpymasterForTeam(team)) return true
  if (!team || !team['agents']) return false
  return team['agents'].some(player => { return player['is_self'] })
}
</script>

<style scoped>
.content {
  position: relative;
  background-color: v-bind("bgColor");
  width: 100vw;
  height: 100vh;
  padding: 10px;

  display: grid;
  grid-template-rows: min-content min-content min-content 1fr;
  grid-template-columns: 1fr 1fr 3fr;
  gap: 10px;
}

.player-info {
  grid-row: 1;
  grid-column: 1 / span 2;

  display: flex;
  flex-wrap: nowrap;
  align-content: center;
  gap: 10px;
}

.player-name {
  height: 100%;
}

.message-info {
  grid-row: 1;
  grid-column: 3;

  display: flex;
  justify-content: center;
  align-content: center;
  align-items: center;
}

.message {
  display: inline-block;
  padding: 5px;
  background-color: white;
  border-radius: 10px;
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
