<template>
  <div>
    <h1 v-if="sock == null">Invalid game ID</h1>
    <div v-else>
      <div>
        Name: <input v-model="name" placeholder="Name" />
      </div>
    </div>
  </div>
</template>

<script setup>
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

</script>
