<template>
  <div class="history">
    <p class="banner">Game Log</p>
    <p :class="[playerTeamClasses[index]]" v-for="(log, index) in props.history" :key="index">
      <span class="player" :class="[playerTeamClasses[index]]">{{ log.player_name }}</span>
      {{ log.description }}
      <span v-if="log.action" class="action" :class="[actionTeamClasses[index]]">{{ log.action }}</span>
    </p>
    <p v-if="props.winner && props.winner == 'blue'" class="blue banner">
      <span class="player blue">BLUE TEAM WINS!</span>
    </p>
    <p v-if="props.winner && props.winner == 'red'" class="red banner">
      <span class="player red">RED TEAM WINS!</span>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  history: Object,
  winner: String
})

const playerTeamClasses = computed(() => {
  let teams = []
  for (const entry of props.history) {
    const team = entry['player_team']
    if (team == 'blue')
      teams.push('blue')
    else if (team == 'red')
      teams.push('red')
    else
      teams.push('')
  }
  return teams
})

const actionTeamClasses = computed(() => {
  let teams = []
  for (const entry of props.history) {
    const team = entry['action_team']
    if (team == 'blue')
      teams.push('blue')
    else if (team == 'red')
      teams.push('red')
    else if (team == 'innocent')
      teams.push('innocent')
    else if (team == 'assassin')
      teams.push('assassin')
    else
      teams.push('none')
  }
  return teams
})
</script>

<style scoped>
.history {
  border-radius: 10px;
  background-color: white;
  overflow: auto;
}

p {
  margin: 0;
  padding: 5px;

  &.blue {
    background-color: #cff9ff;
  }

  &.red {
    background-color: #ffe7d5;
  }
}

.banner {
  text-align: center;
}

span {
  font-weight: bold;
}

.player {
  &.blue {
    color: #3284a3;
  }

  &.red {
    color: #8f2b1c;
  }
}

.action {
  display: inline-block;
  padding: 4px;
  background-color: white;
  text-transform: uppercase;

  &.blue {
    color: #3284a3;
  }

  &.red {
    color: #8f2b1c;
  }

  &.innocent {
    color: #f3d8b5;
  }

  &.assassin {
    color: black;
  }

  &.none {
    color: #909090;
  }
}
</style>
