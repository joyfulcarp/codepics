<template>
  <div>
    <h1>CodePics</h1>
  </div>
  <div>
    <button @click="createGame">Create Game</button>
  </div>
  <div>
    <table>
      <thead>
        <tr>
          <th scope="col">Lobby</th>
          <th scope="col">Players</th>
          <th scope="col">State</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(game, index) in games" :key="index">
          <td>{{ game.game_id }}</td>
          <td>{{ game.players }}</td>
          <td>{{ game.state }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { getGames, postCreateGame } from '@/assets/ts/query.ts'

const router = useRouter()
const games = ref([])
getGames()
  .then((res) => { games.value = res.data.games })
  .catch(console.error)

function createGame() {
  postCreateGame()
    .then((res) => router.push(`/lobby/${res.data.game_id}`))
    .catch(console.error)
}

</script>
