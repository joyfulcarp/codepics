<template>
  <div class="body">
    <div class="info">
      <input id="player_name" v-model="new_name" placeholder="Enter your name" />
      <button class="button" @click="updateName()">Update Name</button>
    </div>
    <div class="game">
      <Game :name="name" :game-id="gameId" />
    </div>
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

<style scoped>
input {
  text-transform: uppercase;
  font-weight: bold;
}

.body {
  position: relative;
  padding-left: 10px;
  padding-right: 10px;
  background-color: green;
}

.info {
  display: flex;
  padding-top: 5px;
  column-gap: 10px;
}

.game {
  padding-top: 10px;
}
</style>
