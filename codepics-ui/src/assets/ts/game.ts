import { io } from 'socket.io-client'
import type { Ref } from 'vue'

export interface PlayerInfo {
  name: string
  is_self: boolean
}

export interface TeamInfo {
  agents: [PlayerInfo]
  spymaster: PlayerInfo
  cards_left: string
}

export interface Teams {
  blue: TeamInfo
  red: TeamInfo
}

export interface CardInfo {
  team: string
  asset: string
  hidden: boolean
}

export interface GameState {
  id: number
  play_state: string
  teams: Teams
  cards: [CardInfo]
  collection: string
  votes: object
}

interface GameUpdate {
  game: GameState
  spymaster_vision: [CardInfo]
}

export class GameEvents {
  socket: io
  game: Ref<GameState>
  is_host: Ref<boolean>
  debug_mode: boolean

  constructor(url: string, game: Ref<GameState>, is_host: Ref<boolean>) {
    this.socket = io(url)
    this.game = game
    this.is_host = is_host
    this.debug_mode = import.meta.env.DEV

    this.registerDebugEvents()
    this.registerEvents()
  }

  registerDebugEvents() {
    if (!this.debug_mode) return;
    this.socket.onAny((eventName, ...args) => {
      console.log(eventName)
      console.log(args)
    })
    this.socket.onAnyOutgoing((eventName, ...args) => {
      console.log(eventName)
      console.log(args)
    })
  }

  debug_fill(gameId: number) {
    this.socket.emit('debug_fill_game', {'game_id': gameId})
  }

  debug_leave_all() {
    this.socket.emit('debug_leave_all', {})
  }

  debug_give_hint(gameId: number, hint: string, count: number) {
    this.socket.emit('debug_give_hint', {
      'game_id': gameId,
      'hint': hint,
      'count': count
    })
  }

  debug_vote(gameId: number, card: number) {
    this.socket.emit('debug_vote', {
      'game_id': gameId,
      'card': card
    })
  }

  debug_reveal(gameId: number, card: number) {
    this.socket.emit('debug_reveal_card', {
      'game_id': gameId,
      'card': card
    })
  }

  registerEvents() {
    this.socket.on('update_game', (data) => this.updateGame(data))
    this.socket.on('update_teams',  (data) => this.updateTeams(data))
    this.socket.on('who_is_host',  (data) => this.updateHost(data))
    this.socket.on('new_turn',  (data) => this.newTurn(data))
    this.socket.on('update_vote',  (data) => this.updateVote(data))
    this.socket.on('update_card',  (data) => this.updateCard(data))
  }

  join(gameId: number, name: string) {
    this.socket.emit('join', {
      'game_id': gameId,
      'name': name
    })
  }

  leave(gameId: number) {
    this.socket.emit('leave', {'game_id': gameId})
  }

  joinTeam(gameId: number, team: string, as_spymaster: boolean) {
    this.socket.emit('switch_team', {
      'game_id': gameId,
      'team': team,
      'as_spymaster': as_spymaster
    })
  }

  startGame(gameId: number) {
    this.socket.emit('start_game', {'game_id': gameId})
  }

  vote(gameId: number, card: number) {
    this.socket.emit('vote', {
      'game_id': gameId,
      'card': card
    })
  }

  reveal(gameId: number, card: number) {
    this.socket.emit('reveal_card', {
      'game_id': gameId,
      'card': card
    })
  }

  updateGame(data: GameUpdate) {
    this.game.value = data.game
    if (data['spymaster_vision'])
      this.game.value['cards'] = data['spymaster_vision']['cards']
  }

  updateTeams(data: GameUpdate)  {
    this.updateGame(data)
  }

  updateHost(data) {
    this.is_host.value = data.is_host;
  }

  newTurn(data) {
    this.updateGame(data)
  }

  updateVote(data) {
    this.updateGame(data)
  }

  updateCard(data) {
    this.updateGame(data)
  }
}
