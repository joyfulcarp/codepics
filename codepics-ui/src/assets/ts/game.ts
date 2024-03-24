import { io } from 'socket.io-client'
import type { Ref } from 'vue'

export interface TeamInfo {
  [members: number]: string
  cards: string
}

export interface Teams {
  blue: TeamInfo
  red: TeamInfo
}

export interface GameState {
  id: number
  lobby_state: string
  teams: Teams
}

interface GameUpdate {
  game: GameState
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

  registerEvents() {
    this.socket.on('update_game', (data) => this.updateGame(data))
    this.socket.on('update_teams',  (data) => this.updateTeams(data))
    this.socket.on('who_is_host',  (data) => this.updateHost(data))
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

  updateGame(data: GameUpdate) {
    this.game.value = data.game
  }

  updateTeams(data: GameUpdate)  {
    this.game.value.teams = data.game.teams
  }

  updateHost(data) {
    this.is_host.value = data.is_host;
  }
}
