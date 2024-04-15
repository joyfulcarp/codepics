<template>
  <div class="row">
    <input class="grow" v-model="hint" :disabled="disableInput" :placeholder="placeholder" />
    <select class="shrink" v-model="count" :disabled="disableInput">
      <option v-for="i in 10">{{ i - 1 }}</option>
    </select>
    <button
      class="shrink alt-button"
      v-show="showGiveHintButton"
      @click="events.giveHint(props.gameId, hint, count)">Give Hint</button>
    <button
      class="shrink button"
      v-show="showEndGuessingButton"
      @click="events.endGuessing(props.gameId)">End Guessing</button>
  </div>
</template>

<script setup lang="ts">
import { GameEvents } from '@/assets/ts/game.ts'

import { computed, ref, watch } from 'vue'

const props = defineProps({
  events: GameEvents,
  gameId: Number,
  isActiveTeam: Boolean,
  isSpymaster: Boolean,
  isSpymasterTurn: Boolean,
  suppliedHint: Object
})

const hint = ref('')
const count = ref(0)

const disableInput = computed(() => {
  return !props.isActiveTeam || !props.isSpymaster || !props.isSpymasterTurn
})

const showGiveHintButton = computed(() => {
  return props.isActiveTeam && props.isSpymaster && props.isSpymasterTurn
})

const showEndGuessingButton = computed(() => {
  return props.isActiveTeam && !props.isSpymaster && !props.isSpymasterTurn
})

const placeholder = computed(() => {
  if (props.isActiveTeam && props.isSpymaster)
    return 'Enter clue here'
  else
    return 'Waiting for hint...'
})

watch(() => props.suppliedHint, (newHint, oldHint) => {
  if (!newHint) return

  const suppliedHint = newHint['hint']
  const suppliedCount = newHint['count']
  if (suppliedHint === undefined || suppliedCount === undefined) {
    hint.value = ''
    count.value = '0'
  } else {
    hint.value = suppliedHint
    count.value = suppliedCount
  }
}, {immediate: true})

</script>

<style scoped>
input {
  height: 30px;
}

select {
  padding-left: 10px;
  padding-right: 10px;
  font-weight: bold;
  border-style: none;
  border-radius: 5px;
  background-color: white;
}

select:disabled {
  appearance: none;
}

.row {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.grow {
  flex-grow: 1;
}
</style>
