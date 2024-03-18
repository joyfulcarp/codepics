<template>
  <div>
    <h1 v-if="sock == null">Invalid game ID</h1>
    <div v-else>
      <div>
        Name: <input v-model="name" placeholder="Name" />
      </div>
      <Team
        :team="'blue'"
        :info="game.teams['blue']"
        @join-team="joinTeam('blue')" />
      <Team
        :team="'red'"
        :info="game.teams['red']"
        @join-team="joinTeam('red')" />
    </div>
  </div>
</template>

<script setup>
import Team from '@/components/Team.vue'

import { io } from 'socket.io-client'

import {
  onUnmounted,
  ref,
  watch
} from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
let gameId
let sock

const name = ref('')
const game = ref({
  'teams': {
    'blue': {
      'members': [],
      'cards': '-'
    },
    'red': {
      'members': [],
      'cards': '-'
    }
  }
})

watch(
  () => route.params.id,
  (newId, oldId) => {
    gameId = parseInt(newId)
  },
  {immediate: true}
)

watch(() => gameId, async (newId, oldId) => {
  if (newId == oldId) return
  if (Number.isNaN(newId)) return

  if (sock == null) {
    sock = io('http://localhost:5001')

    sock.onAny((eventName, ...args) => {
      console.log(eventName)
      console.log(args)
    })
    sock.onAnyOutgoing((eventName, ...args) => {
      console.log(eventName)
      console.log(args)
    })
  }

  if (!isNaN(oldId)) {
    sock.emit('leave', {'game_id': gameId})
  }

  sock.emit('join', {
    'game_id': gameId,
    'name': name.value
  })
}, {immediate: true})

onUnmounted(() => {
  sock.emit('leave', {'game_id': gameId})
})

function joinTeam(team) {
  sock.emit('switch_team', {'game_id': gameId, 'team': team})
}
</script>
