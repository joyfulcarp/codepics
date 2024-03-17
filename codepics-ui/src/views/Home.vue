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
          <td>{{ game.players }}/{{ game.max_players }}</td>
          <td>{{ game.state }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import axios from 'axios'

import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const games = ref([])

function pollGame() {
  const path = 'http://localhost:5001/games'
  axios
    .get(path)
    .then((res) => {
      games.value = res.data.games
    })
    .catch((err) => {
      console.error(err)
    })
}
pollGame()

function createGame(event) {
  const path = 'http://localhost:5001/create_game'
  axios.post(path)
    .then((res) => {
      router.push(`/lobby/${res.data.game_id}`)
    })
}
</script>
