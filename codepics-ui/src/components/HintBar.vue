<template>
  <div class="row">
    <input class="grow" v-model="hint" :disabled="disableInput" :placeholder="placeholder" />
    <select class="shrink" v-model="count" :disabled="disableInput">
      <option v-for="i in 10">{{ i - 1 }}</option>
    </select>
    <button
      class="shrink button"
      v-show="showGiveHintButton"
      @click="events.giveHint(props.gameId, hint.value, count.value)">Give Hint</button>
    <button
      class="shrink alt-button"
      v-show="showEndGuessingButton"
      @click="events.endGuessing(props.gameId)">End Guessing</button>
  </div>
</template>

<script setup lang="ts">
import { GameEvents } from '@/assets/ts/game.ts'

import { computed, ref } from 'vue'

const props = defineProps({
  events: GameEvents,
  gameId: Number,
  allowActions: Boolean,
  isSpymaster: Boolean
})

const hint = ref('')
const count = ref(0)

const disableInput = computed(() => {
  return !props.allowActions || !props.isSpymaster
})

const showGiveHintButton = computed(() => {
  return props.allowActions && props.isSpymaster
})

const showEndGuessingButton = computed(() => {
  return props.allowActions && !props.isSpymaster
})

const placeholder = computed(() => {
  if (props.isSpymaster) {
    return "Enter clue here"
  } else {
    return "Waiting for hint..."
  }
})

</script>

<style>
input {
}

input:disabled {
}

select {
}

select:disabled {
}

.row {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.shrink {
}

.grow {
  flex-grow: 1;
}
</style>
