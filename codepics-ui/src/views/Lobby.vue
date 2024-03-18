<template>
  <div v-if="gameId != null">
    <div v-if="!name">
      <div>
        Choose a name: <input v-model="new_name" placeholder="Enter your name" />
        <button @click="updateName()">Play</button>
      </div>
    </div>
    <div v-else>
      <Game :name="name" :game-id="gameId" />
    </div>
  </div>
  <div v-else>
    <h1>Invalid game ID</h1>
  </div>
</template>

<script setup lang="ts">
import Game from '@/components/Game.vue'

import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const name = ref('Test')
//const name = ref(null)
const new_name = ref(null)

const gameId = ref(null)
watch(
  () => route.params.id,
  (newId, oldId) => {
    if (oldId === newId) return

    const parsed = parseInt(newId)
    if (Number.isNaN(parsed)) {
      gameId.value = null
      return
    }

    gameId.value = parsed
  },
  {immediate: true}
)

function updateName() {
  name.value = new_name.value
}
</script>
